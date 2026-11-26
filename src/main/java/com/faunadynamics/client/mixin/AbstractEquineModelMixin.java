package com.faunadynamics.client.mixin;

import com.faunadynamics.behavior.AnimationStates;
import net.minecraft.client.model.animal.equine.AbstractEquineModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.EquineRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(AbstractEquineModel.class)
public abstract class AbstractEquineModelMixin<T extends EquineRenderState> {
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart leftHindLeg;

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$animateHorseKick(T state, CallbackInfo ci) {
        if (((FdRenderStateAccess) state).faunadynamics$getAction() != AnimationStates.HORSE_KICK) return;
        float kick = (float) Math.sin(state.ageInTicks * 1.5F);
        this.body.xRot += 0.10F;
        this.leftHindLeg.xRot -= 1.05F + Math.max(0.0F, kick) * 0.28F;
        this.rightHindLeg.xRot -= 0.22F;
    }
}
