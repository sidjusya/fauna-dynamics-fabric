package com.faunadynamics.client.mixin;

import com.faunadynamics.client.ClientAnimationData;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Entity.class)
public abstract class EntityEventMixin {
    @Inject(method = "handleEntityEvent", at = @At("HEAD"))
    private void faunadynamics$receiveAnimationEvent(byte event, CallbackInfo ci) {
        Entity entity = (Entity) (Object) this;
        if (entity.level().isClientSide()) {
            ClientAnimationData.accept(entity.getId(), event);
        }
    }

    @Inject(method = "onClientRemoval", at = @At("TAIL"))
    private void faunadynamics$forgetClientEntity(CallbackInfo ci) {
        Entity entity = (Entity) (Object) this;
        ClientAnimationData.forget(entity.getId());
    }
}
