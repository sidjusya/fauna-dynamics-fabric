package com.faunadynamics.client.mixin;

import net.minecraft.client.model.QuadrupedModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.EntityTypes;
import com.faunadynamics.behavior.AnimationStates;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(QuadrupedModel.class)
public abstract class QuadrupedModelMixin<T extends LivingEntityRenderState> {
    @Shadow @Final protected ModelPart head;
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart leftHindLeg;
    @Shadow @Final protected ModelPart rightFrontLeg;
    @Shadow @Final protected ModelPart leftFrontLeg;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateQuadrupeds(T state, CallbackInfo ci) {
        FdRenderStateAccess fd = (FdRenderStateAccess) state;
        int action = fd.faunadynamics$getAction();
        float wave = (float) Math.sin(state.ageInTicks * 0.85F);

        if (action == AnimationStates.RAM_PREPARE || action == AnimationStates.GOAT_PREPARE) {
            this.head.xRot += 0.38F + wave * 0.04F;
            this.body.xRot += 0.05F;
            this.rightHindLeg.xRot -= 0.12F;
            this.leftHindLeg.xRot -= 0.12F;
        } else if (action == AnimationStates.RAM_IMPACT || action == AnimationStates.GOAT_IMPACT) {
            this.head.xRot -= 0.72F;
            this.body.xRot += 0.12F;
            this.rightFrontLeg.xRot -= 0.18F;
            this.leftFrontLeg.xRot -= 0.18F;
        } else if (action == AnimationStates.BULL_CHARGE) {
            this.head.xRot += 0.48F + wave * 0.05F;
            this.body.xRot += 0.10F;
            this.rightFrontLeg.xRot -= 0.16F;
            this.leftFrontLeg.xRot -= 0.16F;
        }

        // Vanilla cows already have small horn parts. Make them visibly heavier on male cows.
        if (fd.faunadynamics$isMale() && state.entityType == EntityTypes.COW) {
            if (this.head.hasChild("right_horn")) {
                ModelPart horn = this.head.getChild("right_horn");
                horn.xScale = 1.35F;
                horn.yScale = 1.85F;
                horn.zScale = 1.45F;
            }
            if (this.head.hasChild("left_horn")) {
                ModelPart horn = this.head.getChild("left_horn");
                horn.xScale = 1.35F;
                horn.yScale = 1.85F;
                horn.zScale = 1.45F;
            }
        }
    }
}
