#include <cmath>
#include <cassert>
#include <iostream>

// Spring-damper system parameters
struct SpringDamper {
    double stiffness;
    double damping;
};

// Ragdoll joint parameters
struct Joint {
    SpringDamper springDamper;
    double restLength;
    double currentLength;
};

// Vehicle wheel parameters
struct Wheel {
    SpringDamper springDamper;
    double restRadius;
    double currentRadius;
};

// Calculate the torque for a spring-damper system
double calculateTorque(const SpringDamper& sd, double displacement) {
    return -sd.stiffness * displacement + sd.damping * (-displacement);
}

// Step the ragdoll joint using a simple Euler integration
void stepRagdollJoint(Joint& joint, double dt) {
    double displacement = joint.currentLength - joint.restLength;
    double torque = calculateTorque(joint.springDamper, displacement);
    joint.currentLength += torque * dt / joint.springDamper.stiffness; // Simplified integration
    assert(std::isfinite(joint.currentLength));
}

// Step the vehicle wheel suspension using a simple Euler integration
void stepVehicleWheel(Wheel& wheel, double dt) {
    double displacement = wheel.currentRadius - wheel.restRadius;
    double torque = calculateTorque(wheel.springDamper, displacement);
    wheel.currentRadius += torque * dt / wheel.springDamper.stiffness; // Simplified integration
    assert(std::isfinite(wheel.currentRadius));
}

int main() {
    // Initialize joint parameters
    Joint joint{ {100.0, 5.0}, 1.0, 1.0 };
    
    // Initialize wheel parameters
    Wheel wheel{ {100.0, 5.0}, 1.0, 1.0 };

    // Time step
    double dt = 0.01;

    // Step the joint
    stepRagdollJoint(joint, dt);

    // Step the wheel
    stepVehicleWheel(wheel, dt);

    std::cout << "Joint length after step: " << joint.currentLength << std::endl;
    std::cout << "Wheel radius after step: " << wheel.currentRadius << std::endl;

    return 0;
}