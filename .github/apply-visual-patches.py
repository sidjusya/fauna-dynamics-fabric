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

# Fix mixin package ownership: shared interfaces must live outside the mixin namespace.
mixin_dir = Path("src/main/java/com/faunadynamics/client/mixin")
accessor_dir = Path("src/main/java/com/faunadynamics/client/accessor")
accessor_dir.mkdir(parents=True, exist_ok=True)
for class_name in ("FdRenderStateAccess", "ModelPartChildrenAccessor"):
    old_path = mixin_dir / (class_name + ".java")
    new_path = accessor_dir / (class_name + ".java")
    accessor_source = old_path.read_text(encoding="utf-8")
    accessor_source = accessor_source.replace("package com.faunadynamics.client.mixin;", "package com.faunadynamics.client.accessor;", 1)
    new_path.write_text(accessor_source, encoding="utf-8")
    old_path.unlink()

for java_path in Path("src/main/java/com/faunadynamics/client").rglob("*.java"):
    java_source = java_path.read_text(encoding="utf-8")
    java_source = java_source.replace("import com.faunadynamics.client.mixin.ModelPartChildrenAccessor;", "import com.faunadynamics.client.accessor.ModelPartChildrenAccessor;")
    if "FdRenderStateAccess" in java_source and "package com.faunadynamics.client.accessor;" not in java_source:
        if "import com.faunadynamics.client.accessor.FdRenderStateAccess;" not in java_source:
            java_source = java_source.replace("package com.faunadynamics.client.mixin;", "package com.faunadynamics.client.mixin;\n\nimport com.faunadynamics.client.accessor.FdRenderStateAccess;", 1)
    java_path.write_text(java_source, encoding="utf-8")

client_config["package"] = "com.faunadynamics.client"
client_config["client"] = [
    "mixin.EntityEventMixin",
    "mixin.EntityRenderStateMixin",
    "mixin.EntityRenderDispatcherMixin",
    "accessor.ModelPartChildrenAccessor",
    "mixin.QuadrupedModelMixin",
    "mixin.AbstractEquineModelMixin",
    "mixin.AdultFelineModelMixin",
    "mixin.BabyFelineModelMixin",
    "mixin.WolfModelMixin",
    "mixin.ChickenModelMixin",
    "mixin.SheepModelMixin"
]
Path("src/main/resources/faunadynamics.client.mixins.json").write_text(json.dumps(client_config, indent=2) + "\n", encoding="utf-8")
print("Moved shared interfaces outside the Mixin package and corrected client mixin registration.")

# Keep the accessor mixin in its own package/config; the shared render-state
# interface is a plain Java API and must not belong to any configured mixin package.
api_dir = Path("src/main/java/com/faunadynamics/api/client")
model_accessor_dir = Path("src/main/java/com/faunadynamics/accessor/client")
api_dir.mkdir(parents=True, exist_ok=True)
model_accessor_dir.mkdir(parents=True, exist_ok=True)
fd_old = Path("src/main/java/com/faunadynamics/client/accessor/FdRenderStateAccess.java")
fd_source = fd_old.read_text(encoding="utf-8").replace("package com.faunadynamics.client.accessor;", "package com.faunadynamics.api.client;", 1)
(api_dir / "FdRenderStateAccess.java").write_text(fd_source, encoding="utf-8")
fd_old.unlink()
mp_old = Path("src/main/java/com/faunadynamics/client/accessor/ModelPartChildrenAccessor.java")
mp_source = mp_old.read_text(encoding="utf-8").replace("package com.faunadynamics.client.accessor;", "package com.faunadynamics.accessor.client;", 1)
(model_accessor_dir / "ModelPartChildrenAccessor.java").write_text(mp_source, encoding="utf-8")
mp_old.unlink()

for java_path in Path("src/main/java").rglob("*.java"):
    java_source = java_path.read_text(encoding="utf-8")
    java_source = java_source.replace("import com.faunadynamics.client.accessor.FdRenderStateAccess;", "import com.faunadynamics.api.client.FdRenderStateAccess;")
    java_source = java_source.replace("import com.faunadynamics.client.accessor.ModelPartChildrenAccessor;", "import com.faunadynamics.accessor.client.ModelPartChildrenAccessor;")
    if "FdRenderStateAccess" in java_source and "package com.faunadynamics.api.client;" not in java_source:
        if "import com.faunadynamics.api.client.FdRenderStateAccess;" not in java_source:
            package_line = next((line for line in java_source.splitlines() if line.startswith("package ")), None)
            if package_line:
                java_source = java_source.replace(package_line, package_line + "\n\nimport com.faunadynamics.api.client.FdRenderStateAccess;", 1)
    java_path.write_text(java_source, encoding="utf-8")

client_config["package"] = "com.faunadynamics.client.mixin"
client_config["client"] = [
    "EntityEventMixin", "EntityRenderStateMixin", "EntityRenderDispatcherMixin",
    "AbstractFelineModelMixin", "QuadrupedModelMixin", "AbstractEquineModelMixin",
    "AdultFelineModelMixin", "BabyFelineModelMixin", "WolfModelMixin", "ChickenModelMixin"
]
Path("src/main/resources/faunadynamics.client.mixins.json").write_text(json.dumps(client_config, indent=2) + "\n", encoding="utf-8")
accessor_config = {
    "required": True,
    "package": "com.faunadynamics.accessor.client",
    "compatibilityLevel": "JAVA_25",
    "client": ["ModelPartChildrenAccessor"],
    "injectors": {"defaultRequire": 1}
}
Path("src/main/resources/faunadynamics.accessor.mixins.json").write_text(json.dumps(accessor_config, indent=2) + "\n", encoding="utf-8")
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
mixins = metadata.setdefault("mixins", [])
accessor_entry = {"config": "faunadynamics.accessor.mixins.json", "environment": "client"}
if accessor_entry not in mixins:
    mixins.append(accessor_entry)
metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print("Separated ordinary render-state API and model accessor mixin into independent packages/configs.")

# Higher ram/bull ratios and a separate, faster ram social-check cadence.
config_path = Path('src/main/java/com/faunadynamics/config/FaunaConfig.java')
config_source = config_path.read_text(encoding='utf-8')
config_source = config_source.replace('public float ramRatio = 0.30F;', 'public float ramRatio = 0.55F;')
config_source = config_source.replace('public float bullRatio = 0.15F;', 'public float bullRatio = 0.45F;')
config_source = config_source.replace('public float ramFightChance = 0.08F;', 'public float ramFightChance = 0.30F;')
if 'public int ramCheckTicks' not in config_source:
    config_source = config_source.replace('public float ramFightChance = 0.30F;', 'public float ramFightChance = 0.30F;\\n    public int ramCheckTicks = 40;')
if 'ramCheckTicks = roundToFiveTicks' not in config_source:
    config_source = config_source.replace('ramFightChance = clamp(ramFightChance, 0.0F, 1.0F);', 'ramFightChance = clamp(ramFightChance, 0.0F, 1.0F);\\n        ramCheckTicks = roundToFiveTicks(clamp(ramCheckTicks, 20, 20 * 60));')
if 'if (current.ramRatio == 0.30F)' not in config_source:
    config_source = config_source.replace('            current.clamp();', '            if (current.ramRatio == 0.30F) current.ramRatio = 0.55F;\\n            if (current.bullRatio == 0.15F) current.bullRatio = 0.45F;\\n            if (current.ramFightChance == 0.08F) current.ramFightChance = 0.30F;\\n            if (current.ramCheckTicks <= 0) current.ramCheckTicks = 40;\\n            current.clamp();')
config_path.write_text(config_source, encoding='utf-8')

source = controller.read_text(encoding='utf-8')
source = source.replace('if (now % config.socialCheckTicks != 0L || level.getRandom().nextFloat() >= config.ramFightChance) return;', 'if (now % config.ramCheckTicks != 0L || level.getRandom().nextFloat() >= config.ramFightChance) return;')
source = source.replace('nearestEntity(sheep, Sheep.class, 10.0,', 'nearestEntity(sheep, Sheep.class, 14.0,')
source = source.replace('nearestEntity(sheep, Sheep.class, 8.0,', 'nearestEntity(sheep, Sheep.class, 12.0,')
controller.write_text(source, encoding='utf-8')

# Remove the extra siblings added by the custom thrown-chicken-egg hatch hook.
main_mixins_path = Path('src/main/resources/faunadynamics.mixins.json')
main_mixins = json.loads(main_mixins_path.read_text(encoding='utf-8'))
main_mixins['mixins'] = [name for name in main_mixins.get('mixins', []) if name != 'ThrownEggMixin']
main_mixins_path.write_text(json.dumps(main_mixins, indent=2) + '\\n', encoding='utf-8')
