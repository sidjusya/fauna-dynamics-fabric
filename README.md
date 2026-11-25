# Fauna Dynamics

A vanilla-friendly animal behavior expansion for Minecraft Java 26.3 (Fabric).

**Current development build:** `0.1.0-alpha.1`

> This is an early playable-behavior prototype, not a finished release. The first pass includes server-side behavior for all seven animal groups. Visible native-model animation rendering, client animation-state networking, and custom ram/bull horn geometry are still in development.

## Supported game setup

- Minecraft Java Edition `26.3`
- Java `25`
- Fabric Loader `0.20.1`
- Fabric API `0.166.2+26.3`
- Fabric Loom `1.19-SNAPSHOT`
- Gradle `9.8.2`

## Animal behavior in this prototype

- **Horses:** adult untamed horses may kick a threat behind them. Default damage is 9 health points (4.5 hearts), with 3 seconds of Slowness.
- **Sheep and rams:** persistent sex traits; adult rams can compete when adult ewes are nearby.
- **Goats:** adult male goats can challenge other adult males with a head-butt style shove.
- **Cows and bulls:** persistent sex traits; bulls retaliate after being hit by a player, then disengage after a limited number of counterattacks.
- **Cats:** litters of 3–6 kittens; short play interactions with dropped items, other cats, and nearby animals.
- **Tamed wolves (dogs):** 50% chance of one pup and 50% chance of 2–3; playful interactions, decorative digging, and non-damaging practice chases.
- **Chickens:** litters of 2–4 chicks on breeding; successful egg hatches can produce 2–3 chicks total. Chicks follow nearby adults.

Litter totals include the first baby already spawned by vanilla Minecraft.

## Visual features not yet implemented

This prototype currently changes server-side behavior and movement. It does not yet render the planned poses on the native models. The following remain on the next implementation pass:

- Horse rear-and-kick pose.
- Ram, goat, and bull head-lowering / charge / impact poses.
- Cat roll-on-back and paw-play poses.
- Dog digging and play poses.
- Visible horn geometry for rams and bulls.
- Client synchronization of action states.

Male/female traits are persisted using vanilla entity tags and currently affect behavior only.

## Source and build

The complete source project is stored in [`.github/fauna-dynamics-source.tar.gz`](.github/fauna-dynamics-source.tar.gz). The Actions workflow extracts it and builds the mod automatically on every push, pull request, or manual dispatch.

The remapped mod JAR is created in `build/libs/` and uploaded as a GitHub Actions artifact when the build succeeds.

## Testing status

The project has not yet passed a full Minecraft 26.3 client test. A successful Gradle build confirms compilation and remapping, not that every behavior has been play-tested in-game.

See [docs/testing-checklist.md](docs/testing-checklist.md) in the source archive.

## License

MIT. See `LICENSE` in the source archive.
