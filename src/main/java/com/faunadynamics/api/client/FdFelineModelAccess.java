package com.faunadynamics.api.client;

import net.minecraft.client.model.geom.ModelPart;

/** Plain API for reading the shared parts of vanilla feline models. */
public interface FdFelineModelAccess {
    ModelPart faunadynamics$getBody();
    ModelPart faunadynamics$getHead();
    ModelPart faunadynamics$getLeftFrontLeg();
    ModelPart faunadynamics$getRightFrontLeg();
    ModelPart faunadynamics$getLeftHindLeg();
    ModelPart faunadynamics$getRightHindLeg();
    ModelPart faunadynamics$getTail1();
    ModelPart faunadynamics$getTail2();
}
