package com.faunadynamics.client.mixin;

import com.faunadynamics.api.client.FdFelineModelAccess;
import com.faunadynamics.behavior.AnimationStates;
import net.minecraft.client.model.animal.feline.BabyFelineModel;
import net.minecraft.client.renderer.entity.state.FelineRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(BabyFelineModel.class)
public abstract class BabyFelineModelMixin<T extends FelineRenderState> {
    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateKittenPlay(T state, CallbackInfo ci) {
        if (((FdRenderStateAccess) state).faunadynamics$getAction() != AnimationStates.CAT_PLAY) return;
        FdFelineModelAccess parts = (FdFelineModelAccess) (Object) this;
        float wave = (float) Math.sin(state.ageInTicks * 1.45F);
        parts.faunadynamics$getBody().zRot += 0.48F * wave;
        parts.faunadynamics$getHead().zRot -= 0.24F * wave;
        parts.faunadynamics$getLeftFrontLeg().xRot -= 0.65F + 0.32F * wave;
        parts.faunadynamics$getRightFrontLeg().xRot -= 0.65F - 0.32F * wave;
        parts.faunadynamics$getLeftHindLeg().xRot += 0.42F * wave;
        parts.faunadynamics$getRightHindLeg().xRot -= 0.42F * wave;
        parts.faunadynamics$getTail1().zRot += 0.25F * wave;
        parts.faunadynamics$getTail2().yRot += 0.40F * wave;
    }
}
