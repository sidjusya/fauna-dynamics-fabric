package com.faunadynamics.client.mixin;

import java.util.HashMap;
import java.util.Map;
import com.faunadynamics.client.mixin.ModelPartChildrenAccessor;
import net.minecraft.client.model.animal.sheep.SheepModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.renderer.entity.state.SheepRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(SheepModel.class)
public abstract class SheepModelMixin {
    @Shadow @Final protected ModelPart head;

    @Inject(method = "<init>", at = @At("TAIL"))
    private void faunadynamics$addRamHorns(ModelPart root, CallbackInfo ci) {
        Map<String, ModelPart> children = ((ModelPartChildrenAccessor) (Object) this.head).faunadynamics$getChildren();
        if (children.containsKey("faunadynamics_left_horn")) return;

        ModelPart left = faunadynamics$makeHorn(-1.0F);
        ModelPart right = faunadynamics$makeHorn(1.0F);
        left.setPos(-2.6F, -3.4F, -1.2F);
        right.setPos(2.6F, -3.4F, -1.2F);
        left.zRot = -0.48F;
        right.zRot = 0.48F;
        left.yRot = -0.10F;
        right.yRot = 0.10F;
        left.visible = false;
        right.visible = false;
        left.setInitialPose(left.storePose());
        right.setInitialPose(right.storePose());
        children.put("faunadynamics_left_horn", left);
        children.put("faunadynamics_right_horn", right);
    }

    @Inject(method = "setupAnim", at = @At("TAIL"))
    private void faunadynamics$showRamHorns(SheepRenderState state, CallbackInfo ci) {
        boolean male = ((FdRenderStateAccess) state).faunadynamics$isMale();
        if (this.head.hasChild("faunadynamics_left_horn")) {
            this.head.getChild("faunadynamics_left_horn").visible = male;
            this.head.getChild("faunadynamics_right_horn").visible = male;
        }
    }

    private static ModelPart faunadynamics$makeHorn(float direction) {
        return new ModelPart(
                CubeListBuilder.create()
                        .texOffs(0, 16)
                        .addBox(-0.65F, -0.5F, -0.5F, 1.3F, 2.8F, 1.3F)
                        .texOffs(0, 16)
                        .addBox(-0.55F, 1.6F, -0.45F, 1.1F, 1.3F, 1.1F)
                        .build(),
                new HashMap<>()
        );
    }
}
