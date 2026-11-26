package com.faunadynamics.client.mixin;

import java.util.HashMap;
import java.util.Map;
import com.faunadynamics.accessor.client.ModelPartChildrenAccessor;
import net.minecraft.client.model.QuadrupedModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
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

        if (state.entityType == EntityTypes.COW) {
            faunadynamics$scaleCowHorns(fd.faunadynamics$isMale());
        } else if (state.entityType == EntityTypes.SHEEP) {
            faunadynamics$updateRamHorns(fd.faunadynamics$isMale());
        }
    }

    private void faunadynamics$scaleCowHorns(boolean male) {
        if (this.head.hasChild("right_horn")) {
            ModelPart horn = this.head.getChild("right_horn");
            horn.xScale = male ? 1.35F : 1.0F;
            horn.yScale = male ? 1.85F : 1.0F;
            horn.zScale = male ? 1.45F : 1.0F;
        }
        if (this.head.hasChild("left_horn")) {
            ModelPart horn = this.head.getChild("left_horn");
            horn.xScale = male ? 1.35F : 1.0F;
            horn.yScale = male ? 1.85F : 1.0F;
            horn.zScale = male ? 1.45F : 1.0F;
        }
    }

    private void faunadynamics$updateRamHorns(boolean male) {
        Map<String, ModelPart> children = ((ModelPartChildrenAccessor) (Object) this.head).faunadynamics$getChildren();
        if (!children.containsKey("faunadynamics_left_horn")) {
            ModelPart left = faunadynamics$makeHorn();
            ModelPart right = faunadynamics$makeHorn();
            left.setPos(-2.6F, -3.4F, -1.2F);
            right.setPos(2.6F, -3.4F, -1.2F);
            left.zRot = -0.48F;
            right.zRot = 0.48F;
            left.yRot = -0.10F;
            right.yRot = 0.10F;
            left.setInitialPose(left.storePose());
            right.setInitialPose(right.storePose());
            children.put("faunadynamics_left_horn", left);
            children.put("faunadynamics_right_horn", right);
        }
        this.head.getChild("faunadynamics_left_horn").visible = male;
        this.head.getChild("faunadynamics_right_horn").visible = male;
    }

    private static ModelPart faunadynamics$makeHorn() {
        var cubes = CubeListBuilder.create()
                .texOffs(0, 16)
                .addBox(-0.65F, -0.5F, -0.5F, 1.3F, 2.8F, 1.3F)
                .texOffs(0, 16)
                .addBox(-0.55F, 1.6F, -0.45F, 1.1F, 1.3F, 1.1F)
                .getCubes();
        var baked = cubes.stream().map(cube -> cube.bake(64, 32)).toList();
        return new ModelPart(baked, new HashMap<>());
    }
}
