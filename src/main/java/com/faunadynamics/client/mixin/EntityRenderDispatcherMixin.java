package com.faunadynamics.client.mixin;

import com.faunadynamics.client.ClientAnimationData;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(EntityRenderDispatcher.class)
public abstract class EntityRenderDispatcherMixin {
    @Inject(method = "extractEntity", at = @At("TAIL"))
    private void faunadynamics$copyClientAnimation(Entity entity, float partialTicks,
            CallbackInfoReturnable<EntityRenderState> cir) {
        EntityRenderState renderState = cir.getReturnValue();
        if (renderState instanceof LivingEntityRenderState) {
            FdRenderStateAccess access = (FdRenderStateAccess) renderState;
            int id = entity.getId();
            access.faunadynamics$setData(id, ClientAnimationData.action(id), ClientAnimationData.isMale(id));
        }
    }
}
