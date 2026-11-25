# Fauna Dynamics

Vanilla-friendly animal behavior expansion for Minecraft Java 26.3 (Fabric).

**Status:** early source prototype (`0.1.0-alpha.1`). It is not yet a verified playable release. The current code contains server-side behavior prototypes and breeding/egg-hatch mixins. Visible native-model animations, horn rendering, client animation synchronization, and in-game testing remain in progress.

## Target
- Minecraft Java 26.3
- Java 25
- Fabric Loader 0.20.1
- Fabric Loom 1.19-SNAPSHOT
- Fabric API 0.166.2+26.3

## Build
Use JDK 25 and the Gradle version pinned by the wrapper. Run `./gradlew --no-daemon clean build`. The remapped JAR is produced in `build/libs/`.

See `docs/behavior-design.md`, `docs/animation-plan.md`, and `docs/testing-checklist.md` for current behavior scope and outstanding work.
