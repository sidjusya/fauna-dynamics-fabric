package com.faunadynamics.client.mixin;

import net.minecraft.client.model.animal.chicken.ChickenModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.ChickenRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ChickenModel.class)
public abstract class ChickenModelMixin {
    @Shadow @Final private ModelPart rightWing;
    @Shadow @Final private ModelPart leftWing;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateChicks(ChickenRenderState state, CallbackInfo ci) {
        if (!state.isBaby || state.walkAnimationSpeed < 0.12F) return;
        float flap = (float) Math.sin(state.ageInTicks * 1.9F) * 0.22F;
        this.rightWing.zRot += flap;
        this.leftWing.zRot -= flap;
    }
}
