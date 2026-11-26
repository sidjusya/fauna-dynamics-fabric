from pathlib import Path
import json

NL = chr(10)
BS = chr(92)

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
    "AdultFelineModelMixin", "BabyFelineModelMixin", "WolfModelMixin", "ChickenModelMixin",
    "SheepModelMixin"
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
main_mixins_raw = main_mixins_path.read_text(encoding='utf-8').replace(BS + BS + 'n', NL).replace(BS + 'n', NL)
main_mixins = json.loads(main_mixins_raw)
main_mixins['mixins'] = [name for name in main_mixins.get('mixins', []) if name != 'ThrownEggMixin']
main_mixins_path.write_text(json.dumps(main_mixins, indent=2) + '\\n', encoding='utf-8')

# Final pass: fix prior escaped-newline inserts, migrate saved sex tags, and drive
# the horse kick from the event clock rather than the animal's lifetime age.
NL = chr(10)
BS = chr(92)

config_path = Path('src/main/java/com/faunadynamics/config/FaunaConfig.java')
config_source = config_path.read_text(encoding='utf-8').replace(BS + BS + 'n', NL).replace(BS + 'n', NL)
config_source = config_source.replace('public float ramRatio = 0.30F;', 'public float ramRatio = 0.60F;')
config_source = config_source.replace('public float ramRatio = 0.55F;', 'public float ramRatio = 0.60F;')
config_source = config_source.replace('public float bullRatio = 0.15F;', 'public float bullRatio = 0.50F;')
config_source = config_source.replace('public float bullRatio = 0.45F;', 'public float bullRatio = 0.50F;')
config_source = config_source.replace('public float ramFightChance = 0.08F;', 'public float ramFightChance = 0.30F;')
if 'public int ramCheckTicks' not in config_source:
    config_source = config_source.replace('public float ramFightChance = 0.30F;', 'public float ramFightChance = 0.30F;' + NL + '    public int ramCheckTicks = 40;')
if 'ramCheckTicks = roundToFiveTicks' not in config_source:
    config_source = config_source.replace('ramFightChance = clamp(ramFightChance, 0.0F, 1.0F);', 'ramFightChance = clamp(ramFightChance, 0.0F, 1.0F);' + NL + '        ramCheckTicks = roundToFiveTicks(clamp(ramCheckTicks, 20, 20 * 60));')
migration = NL.join([
    '            // Migrate only untouched defaults; preserve settings explicitly changed by the user.',
    '            if (current.ramRatio == 0.30F || current.ramRatio == 0.55F) current.ramRatio = 0.60F;',
    '            if (current.bullRatio == 0.15F || current.bullRatio == 0.45F) current.bullRatio = 0.50F;',
    '            if (current.ramFightChance == 0.08F) current.ramFightChance = 0.30F;',
    '            if (current.ramCheckTicks <= 0) current.ramCheckTicks = 40;'
])
if 'Migrate only untouched defaults' not in config_source:
    config_source = config_source.replace('            current.clamp();', migration + NL + '            current.clamp();')
config_path.write_text(config_source, encoding='utf-8')

controller_source = controller.read_text(encoding='utf-8')
controller_source = controller_source.replace('if (now % config.socialCheckTicks != 0L || level.getRandom().nextFloat() >= config.ramFightChance) return;', 'if (now % config.ramCheckTicks != 0L || level.getRandom().nextFloat() >= config.ramFightChance) return;')
controller_source = controller_source.replace('nearestEntity(sheep, Sheep.class, 10.0,', 'nearestEntity(sheep, Sheep.class, 14.0,')
controller_source = controller_source.replace('nearestEntity(sheep, Sheep.class, 8.0,', 'nearestEntity(sheep, Sheep.class, 12.0,')
controller_source = controller_source.replace('AnimationStates.HORSE_KICK, now, 18L', 'AnimationStates.HORSE_KICK, now, 22L')
controller.write_text(controller_source, encoding='utf-8')

tags_path = Path('src/main/java/com/faunadynamics/behavior/AnimalTags.java')
tags_path.write_text('''package com.faunadynamics.behavior;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;

/** Persistent vanilla entity tags used for lightweight per-animal traits. */
public final class AnimalTags {
    private static final String SEX_SET = "faunadynamics.sex_set";
    private static final String MALE = "faunadynamics.male";
    private static final String SEX_REVISION = "faunadynamics.sex_revision_2";

    private AnimalTags() {
    }

    public static boolean ensureMale(Entity entity, Level level, float chance) {
        // Re-roll animals assigned by older, much lower default ratios, once only.
        if (!entity.entityTags().contains(SEX_REVISION)) {
            entity.removeTag(SEX_SET);
            entity.removeTag(MALE);
            entity.addTag(SEX_REVISION);
        }
        if (!entity.entityTags().contains(SEX_SET)) {
            entity.addTag(SEX_SET);
            if (level.getRandom().nextFloat() < chance) entity.addTag(MALE);
        }
        return entity.entityTags().contains(MALE);
    }

    public static boolean isMale(Entity entity) {
        return entity.entityTags().contains(MALE);
    }
}
''', encoding='utf-8')

Path('src/main/java/com/faunadynamics/api/client/FdRenderStateAccess.java').write_text('''package com.faunadynamics.api.client;

/** Extra per-frame data copied from the live entity into Minecraft's render-state snapshot. */
public interface FdRenderStateAccess {
    void faunadynamics$setData(int entityId, int action, boolean male, int actionAgeTicks);
    int faunadynamics$getAction();
    int faunadynamics$getActionAgeTicks();
    boolean faunadynamics$isMale();
}
''', encoding='utf-8')

Path('src/main/java/com/faunadynamics/client/ClientAnimationData.java').write_text('''package com.faunadynamics.client;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/** Client mirror of short animation cues sent by the authoritative server. */
public final class ClientAnimationData {
    private static final Map<Integer, ActionCue> ACTIONS = new HashMap<>();
    private static final Set<Integer> MALES = new HashSet<>();
    private ClientAnimationData() {}

    public static void accept(int entityId, byte rawEvent, int entityTick) {
        int event = rawEvent & 0xFF;
        if (event == 100) ACTIONS.remove(entityId);
        else if (event >= 101 && event <= 109) ACTIONS.put(entityId, new ActionCue(event - 100, entityTick));
        else if (event == 120) MALES.add(entityId);
        if (ACTIONS.size() > 4096) ACTIONS.clear();
        if (MALES.size() > 8192) MALES.clear();
    }

    public static int action(int entityId) {
        ActionCue cue = ACTIONS.get(entityId);
        return cue == null ? 0 : cue.action();
    }

    public static int actionAgeTicks(int entityId, int entityTick) {
        ActionCue cue = ACTIONS.get(entityId);
        return cue == null ? 0 : Math.max(0, entityTick - cue.startedAtTick());
    }

    public static boolean isMale(int entityId) { return MALES.contains(entityId); }
    public static void forget(int entityId) { ACTIONS.remove(entityId); MALES.remove(entityId); }
    private record ActionCue(int action, int startedAtTick) {}
}
''', encoding='utf-8')

event_path = Path('src/main/java/com/faunadynamics/client/mixin/EntityEventMixin.java')
event_source = event_path.read_text(encoding='utf-8').replace('ClientAnimationData.accept(entity.getId(), event);', 'ClientAnimationData.accept(entity.getId(), event, entity.tickCount);')
event_path.write_text(event_source, encoding='utf-8')

state_path = Path('src/main/java/com/faunadynamics/client/mixin/EntityRenderStateMixin.java')
state_path.write_text('''package com.faunadynamics.client.mixin;

import com.faunadynamics.api.client.FdRenderStateAccess;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import net.minecraft.client.renderer.entity.state.EntityRenderState;

@Mixin(EntityRenderState.class)
public abstract class EntityRenderStateMixin implements FdRenderStateAccess {
    @Unique private int faunadynamics$entityId = -1;
    @Unique private int faunadynamics$action;
    @Unique private int faunadynamics$actionAgeTicks;
    @Unique private boolean faunadynamics$male;
    @Override public void faunadynamics$setData(int entityId, int action, boolean male, int actionAgeTicks) {
        this.faunadynamics$entityId = entityId;
        this.faunadynamics$action = action;
        this.faunadynamics$male = male;
        this.faunadynamics$actionAgeTicks = actionAgeTicks;
    }
    @Override public int faunadynamics$getAction() { return this.faunadynamics$action; }
    @Override public int faunadynamics$getActionAgeTicks() { return this.faunadynamics$actionAgeTicks; }
    @Override public boolean faunadynamics$isMale() { return this.faunadynamics$male; }
}
''', encoding='utf-8')

dispatcher_path = Path('src/main/java/com/faunadynamics/client/mixin/EntityRenderDispatcherMixin.java')
dispatcher_source = dispatcher_path.read_text(encoding='utf-8')
dispatcher_source = dispatcher_source.replace('import com.faunadynamics.client.ClientAnimationData;', 'import com.faunadynamics.client.ClientAnimationData;' + NL + 'import com.faunadynamics.api.client.FdRenderStateAccess;')
dispatcher_source = dispatcher_source.replace('access.faunadynamics$setData(id, ClientAnimationData.action(id), ClientAnimationData.isMale(id));', 'access.faunadynamics$setData(id, ClientAnimationData.action(id), ClientAnimationData.isMale(id), ClientAnimationData.actionAgeTicks(id, entity.tickCount));')
dispatcher_path.write_text(dispatcher_source, encoding='utf-8')

horse_path = Path('src/main/java/com/faunadynamics/client/mixin/AbstractEquineModelMixin.java')
horse_path.write_text('''package com.faunadynamics.client.mixin;

import com.faunadynamics.api.client.FdRenderStateAccess;
import com.faunadynamics.behavior.AnimationStates;
import net.minecraft.client.model.animal.equine.AbstractEquineModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.EquineRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(AbstractEquineModel.class)
public abstract class AbstractEquineModelMixin<T extends EquineRenderState> {
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart leftHindLeg;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateHorseKick(T state, CallbackInfo ci) {
        FdRenderStateAccess access = (FdRenderStateAccess) state;
        if (access.faunadynamics$getAction() != AnimationStates.HORSE_KICK) return;
        float progress = Math.min(22.0F, access.faunadynamics$getActionAgeTicks()) / 22.0F;
        float lift = smoothstep(0.0F, 0.28F, progress) * (1.0F - smoothstep(0.68F, 0.96F, progress));
        float kick = smoothstep(0.18F, 0.36F, progress) * (1.0F - smoothstep(0.48F, 0.72F, progress));
        this.body.y -= 5.2F * lift;
        this.body.xRot += 0.48F * lift;
        this.leftHindLeg.xRot -= 0.30F * lift + 1.45F * kick;
        this.rightHindLeg.xRot -= 0.26F * lift + 1.30F * kick;
        this.leftHindLeg.zRot -= 0.10F * kick;
        this.rightHindLeg.zRot += 0.10F * kick;
    }

    private static float smoothstep(float edge0, float edge1, float value) {
        float t = Math.max(0.0F, Math.min(1.0F, (value - edge0) / (edge1 - edge0)));
        return t * t * (3.0F - 2.0F * t);
    }
}
''', encoding='utf-8')

# Remove any old extra-chick handler from active mixins; vanilla hatch now makes one chick.
main_mixins_path = Path('src/main/resources/faunadynamics.mixins.json')
main_mixins_raw = main_mixins_path.read_text(encoding='utf-8').replace(BS + BS + 'n', NL).replace(BS + 'n', NL)
main_mixins = json.loads(main_mixins_raw)
main_mixins['mixins'] = [name for name in main_mixins.get('mixins', []) if name != 'ThrownEggMixin']
main_mixins_path.write_text(json.dumps(main_mixins, indent=2) + NL, encoding='utf-8')
print('Applied sex migration, timed horse kick, increased ram/bull odds, and vanilla single-chick egg hatching.')


# Follow-up fixes from in-game testing: move both rear hoof/leg assemblies backward
# during the kick, and explicitly register the sheep-specific horn hook.
horse_source = horse_path.read_text(encoding="utf-8")
horse_source = horse_source.replace(
    "this.leftHindLeg.xRot -= 0.30F * lift + 1.45F * kick;",
    "this.leftHindLeg.xRot += 0.38F * lift + 1.55F * kick;"
)
horse_source = horse_source.replace(
    "this.rightHindLeg.xRot -= 0.26F * lift + 1.30F * kick;",
    "this.rightHindLeg.xRot += 0.42F * lift + 1.62F * kick;"
)
horse_source = horse_source.replace(
    "this.leftHindLeg.zRot -= 0.10F * kick;",
    "this.leftHindLeg.zRot += 0.08F * kick;"
)
horse_source = horse_source.replace(
    "this.rightHindLeg.zRot += 0.10F * kick;",
    "this.rightHindLeg.zRot -= 0.08F * kick;"
)
horse_path.write_text(horse_source, encoding="utf-8")

# The dedicated SheepModel hook adds the horns directly to the sheep head model.
# QuadrupedModelMixin also knows how to toggle them; both paths share the same names
# and guard against adding duplicate parts.
if "SheepModelMixin" not in client_config["client"]:
    client_config["client"].append("SheepModelMixin")
Path("src/main/resources/faunadynamics.client.mixins.json").write_text(
    json.dumps(client_config, indent=2) + NL, encoding="utf-8"
)

# Make ram impacts clearly separate the two animals instead of only nudging them.
controller_source = controller.read_text(encoding="utf-8")
old_ram_shove = "shovePair(sheep, rival, 0.48);"
if old_ram_shove not in controller_source:
    raise SystemExit("Ram shove call was not found; refusing to silently skip knockback tuning.")
controller_source = controller_source.replace(old_ram_shove, "shovePair(sheep, rival, 0.92);", 1)
controller.write_text(controller_source, encoding="utf-8")

print("Applied rear-hoof kick direction, registered sheep ram horns, and strengthened ram collision knockback.")
