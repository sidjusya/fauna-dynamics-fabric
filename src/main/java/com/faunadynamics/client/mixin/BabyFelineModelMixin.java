package com.faunadynamics.client.mixin;

import com.faunadynamics.behavior.AnimationStates;
import net.minecraft.client.model.animal.feline.BabyFelineModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.FelineRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(BabyFelineModel.class)
public abstract class BabyFelineModelMixin<T extends FelineRenderState> {
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart head;
    @Shadow @Final protected ModelPart leftFrontLeg;
    @Shadow @Final protected ModelPart rightFrontLeg;
    @Shadow @Final protected ModelPart leftHindLeg;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart tail1;
    @Shadow @Final protected ModelPart tail2;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateKittenPlay(T state, CallbackInfo ci) {
        if (((FdRenderStateAccess) state).faunadynamics$getAction() != AnimationStates.CAT_PLAY) return;
        float wave = (float) Math.sin(state.ageInTicks * 1.45F);
        this.body.zRot += 0.48F * wave;
        this.head.zRot -= 0.24F * wave;
        this.leftFrontLeg.xRot -= 0.65F + 0.32F * wave;
        this.rightFrontLeg.xRot -= 0.65F - 0.32F * wave;
        this.leftHindLeg.xRot += 0.42F * wave;
        this.rightHindLeg.xRot -= 0.42F * wave;
        this.tail1.zRot += 0.25F * wave;
        this.tail2.yRot += 0.40F * wave;
    }
}
