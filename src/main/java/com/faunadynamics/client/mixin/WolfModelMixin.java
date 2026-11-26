package com.faunadynamics.client.mixin;

import com.faunadynamics.behavior.AnimationStates;
import net.minecraft.client.model.animal.wolf.WolfModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.WolfRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(WolfModel.class)
public abstract class WolfModelMixin {
    @Shadow @Final protected ModelPart head;
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart tail;
    @Shadow @Final protected ModelPart rightFrontLeg;
    @Shadow @Final protected ModelPart leftFrontLeg;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart leftHindLeg;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateDogActions(WolfRenderState state, CallbackInfo ci) {
        int action = ((FdRenderStateAccess) state).faunadynamics$getAction();
        float wave = (float) Math.sin(state.ageInTicks * 1.7F);
        if (action == AnimationStates.DOG_DIG) {
            this.rightFrontLeg.xRot = -0.95F - 0.28F * wave;
            this.leftFrontLeg.xRot = -0.95F + 0.28F * wave;
            this.head.xRot += 0.12F;
            this.body.xRot += 0.05F;
        } else if (action == AnimationStates.DOG_PLAY) {
            this.body.zRot += 0.18F * wave;
            this.head.xRot -= 0.18F;
            this.rightFrontLeg.xRot -= 0.40F + 0.22F * wave;
            this.leftFrontLeg.xRot -= 0.40F - 0.22F * wave;
            this.rightHindLeg.xRot += 0.18F * wave;
            this.leftHindLeg.xRot -= 0.18F * wave;
            this.tail.zRot += 0.24F * wave;
        }
    }
}
