package com.faunadynamics.client.mixin;

import com.faunadynamics.api.client.FdFelineModelAccess;
import net.minecraft.client.model.animal.feline.AbstractFelineModel;
import net.minecraft.client.model.geom.ModelPart;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;

/** Exposes parts declared by the common vanilla parent, not the adult/kitten subclasses. */
@Mixin(AbstractFelineModel.class)
public abstract class AbstractFelineModelMixin implements FdFelineModelAccess {
    @Shadow @Final protected ModelPart body;
    @Shadow @Final protected ModelPart head;
    @Shadow @Final protected ModelPart leftFrontLeg;
    @Shadow @Final protected ModelPart rightFrontLeg;
    @Shadow @Final protected ModelPart leftHindLeg;
    @Shadow @Final protected ModelPart rightHindLeg;
    @Shadow @Final protected ModelPart tail1;
    @Shadow @Final protected ModelPart tail2;

    @Override public ModelPart faunadynamics$getBody() { return this.body; }
    @Override public ModelPart faunadynamics$getHead() { return this.head; }
    @Override public ModelPart faunadynamics$getLeftFrontLeg() { return this.leftFrontLeg; }
    @Override public ModelPart faunadynamics$getRightFrontLeg() { return this.rightFrontLeg; }
    @Override public ModelPart faunadynamics$getLeftHindLeg() { return this.leftHindLeg; }
    @Override public ModelPart faunadynamics$getRightHindLeg() { return this.rightHindLeg; }
    @Override public ModelPart faunadynamics$getTail1() { return this.tail1; }
    @Override public ModelPart faunadynamics$getTail2() { return this.tail2; }
}
