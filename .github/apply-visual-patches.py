from pathlib import Path
import json

ROOT = Path("src/main/java/com/faunadynamics/behavior")
controller = ROOT / "AnimalBehaviorController.java"
source = controller.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    source = source.replace(old, new)

replace_once(
'''    private static boolean ensureSex(Mob animal, ServerLevel level, float maleChance) {
        return AnimalTags.ensureMale(animal, level, maleChance);
    }''',
'''    private static boolean ensureSex(Mob animal, ServerLevel level, float maleChance) {
        boolean male = AnimalTags.ensureMale(animal, level, maleChance);
        // Re-send occasionally so players who join later also learn the persistent sex trait.
        if (male && level.getGameTime() % 100L == 0L) {
            level.broadcastEntityEvent(animal, (byte) 120);
        }
        return male;
    }''',
"ensureSex"
)

replace_once(
'''    private static void playAnimation(Mob mob, int action, long now, long duration) {
        // Logical action state. A dedicated client payload will feed native model poses in a later pass.
        ACTIVE_ACTIONS.put(mob.getUUID(), action);
        ACTION_END_TICK.put(mob.getUUID(), now + duration);
    }''',
'''    private static void playAnimation(Mob mob, int action, long now, long duration) {
        int previous = ACTIVE_ACTIONS.getOrDefault(mob.getUUID(), AnimationStates.NONE);
        ACTIVE_ACTIONS.put(mob.getUUID(), action);
        ACTION_END_TICK.put(mob.getUUID(), now + duration);
        if (previous != action && mob.level() instanceof ServerLevel serverLevel) {
            serverLevel.broadcastEntityEvent(mob, (byte) (100 + action));
        }
    }''',
"playAnimation"
)

replace_once(
'''    private static void clearExpiredAction(Mob mob, long now) {
        Long endTick = ACTION_END_TICK.get(mob.getUUID());
        if (endTick != null && now >= endTick) {
            ACTIVE_ACTIONS.remove(mob.getUUID());
            ACTION_END_TICK.remove(mob.getUUID());
        }
    }''',
'''    private static void clearExpiredAction(Mob mob, long now) {
        Long endTick = ACTION_END_TICK.get(mob.getUUID());
        if (endTick != null && now >= endTick) {
            Integer previous = ACTIVE_ACTIONS.remove(mob.getUUID());
            ACTION_END_TICK.remove(mob.getUUID());
            if (previous != null && mob.level() instanceof ServerLevel serverLevel) {
                serverLevel.broadcastEntityEvent(mob, (byte) 100);
            }
        }
    }''',
"clearExpiredAction"
)

controller.write_text(source, encoding="utf-8")

metadata_path = Path("src/main/resources/fabric.mod.json")
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
mixins = metadata.setdefault("mixins", [])
client_entry = {"config": "faunadynamics.client.mixins.json", "environment": "client"}
if client_entry not in mixins and "faunadynamics.client.mixins.json" not in mixins:
    mixins.append(client_entry)
metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

client_config = {
    "required": True,
    "package": "com.faunadynamics.client.mixin",
    "compatibilityLevel": "JAVA_25",
    "client": [
        "EntityEventMixin",
        "EntityRenderStateMixin",
        "EntityRenderDispatcherMixin",
        "ModelPartChildrenAccessor",
        "QuadrupedModelMixin",
        "AbstractEquineModelMixin",
        "AdultFelineModelMixin",
        "BabyFelineModelMixin",
        "WolfModelMixin",
        "ChickenModelMixin",
        "SheepModelMixin"
    ],
    "injectors": {"defaultRequire": 1}
}
Path("src/main/resources/faunadynamics.client.mixins.json").write_text(
    json.dumps(client_config, indent=2) + "\n", encoding="utf-8"
)

print("Connected server animation events to client render states and registered native model mixins.")
