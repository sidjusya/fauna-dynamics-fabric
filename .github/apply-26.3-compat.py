from pathlib import Path

ROOT = Path("src/main/java/com/faunadynamics")

def replace(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Expected compatibility target not found in {file}")
    file.write_text(text.replace(old, new), encoding="utf-8")

replace(
    "mixin/AnimalBreedingMixin.java",
    "baby.moveTo(parent.getX() + Math.cos(angle) * radius, parent.getY(),",
    "baby.snapTo(parent.getX() + Math.cos(angle) * radius, parent.getY(),",
)

replace(
    "mixin/ThrownEggMixin.java",
    "import net.minecraft.world.entity.EntityType;\n",
    "import net.minecraft.world.entity.EntitySpawnReason;\nimport net.minecraft.world.entity.EntityTypes;\n",
)
replace(
    "mixin/ThrownEggMixin.java",
    "Chicken chick = new Chicken(EntityType.CHICKEN, level);",
    "Chicken chick = EntityTypes.CHICKEN.create(level, EntitySpawnReason.TRIGGERED);\n            if (chick == null) continue;",
)
replace(
    "mixin/ThrownEggMixin.java",
    "chick.moveTo(egg.getX() + Math.cos(angle) * radius, egg.getY(),",
    "chick.snapTo(egg.getX() + Math.cos(angle) * radius, egg.getY(),",
)

replace(
    "behavior/AnimalBehaviorController.java",
    "level.getEntities(null, baby.getBoundingBox().inflate(12.0),",
    "level.getEntities((Entity) null, baby.getBoundingBox().inflate(12.0),",
)
replace(
    "behavior/AnimalBehaviorController.java",
    "private static <T extends LivingEntity> T nearestEntity(Entity source, Class<T> type, double range,",
    "private static <T extends Entity> T nearestEntity(Entity source, Class<T> type, double range,",
)

print("Applied Minecraft 26.3 compatibility fixes.")
