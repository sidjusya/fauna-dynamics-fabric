package com.faunadynamics.client.mixin;

/** Extra per-frame data copied from the live entity into Minecraft's render-state snapshot. */
public interface FdRenderStateAccess {
    void faunadynamics$setData(int entityId, int action, boolean male);
    int faunadynamics$getAction();
    boolean faunadynamics$isMale();
}
