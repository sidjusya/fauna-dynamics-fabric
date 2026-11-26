package com.faunadynamics.client.mixin;

import com.faunadynamics.behavior.AnimationStates;
import net.minecraft.client.model.animal.feline.AdultFelineModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.FelineRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(AdultFelineModel.class)
public abstract class AdultFelineModelMixin<T extends FelineRenderState> {
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart head;
    @Shadow @Final protected ModelPart leftFrontLeg;
    @Shadow @Final protected ModelPart rightFrontLeg;
    @Shadow @Final protected ModelPart leftHindLeg;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart tail1;
    @Shadow @Final protected ModelPart tail2;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateCatPlay(T state, CallbackInfo ci) {
        if (((FdRenderStateAccess) state).faunadynamics$getAction() != AnimationStates.CAT_PLAY) return;
        float wave = (float) Math.sin(state.ageInTicks * 1.25F);
        this.body.zRot += 0.38F * wave;
        this.head.zRot -= 0.20F * wave;
        this.leftFrontLeg.xRot -= 0.50F + 0.28F * wave;
        this.rightFrontLeg.xRot -= 0.50F - 0.28F * wave;
        this.leftHindLeg.xRot += 0.35F * wave;
        this.rightHindLeg.xRot -= 0.35F * wave;
        this.tail1.zRot += 0.22F * wave;
        this.tail2.yRot += 0.35F * wave;
    }
}
