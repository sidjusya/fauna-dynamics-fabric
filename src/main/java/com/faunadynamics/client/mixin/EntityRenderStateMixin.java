package com.faunadynamics.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import net.minecraft.client.renderer.entity.state.EntityRenderState;

@Mixin(EntityRenderState.class)
public abstract class EntityRenderStateMixin implements FdRenderStateAccess {
    @Unique private int faunadynamics$entityId = -1;
    @Unique private int faunadynamics$action;
    @Unique private boolean faunadynamics$male;

    @Override
    public void faunadynamics$setData(int entityId, int action, boolean male) {
        this.faunadynamics$entityId = entityId;
        this.faunadynamics$action = action;
        this.faunadynamics$male = male;
    }

    @Override
    public int faunadynamics$getAction() {
        return this.faunadynamics$action;
    }

    @Override
    public boolean faunadynamics$isMale() {
        return this.faunadynamics$male;
    }
}
