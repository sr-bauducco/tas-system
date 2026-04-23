// Inside your TreatmentContext record
public goals.context.EmergencyContext toEmergencyContext() {
    return new goals.context.EmergencyContext(this.internetAvailable(), false);
}