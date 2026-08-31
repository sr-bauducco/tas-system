package api;

public class TelemetryLogger {
    // Imprime um JSON limpo direto no stdout para o Docker capturar
    public static void logEvent(String service, String type, String label, String state) {
        long timestamp = System.currentTimeMillis();
        String json = String.format(
            "{\"telemetry\": true, \"timestamp\": %d, \"service\": \"%s\", \"type\": \"%s\", \"label\": \"%s\", \"state\": \"%s\"}",
            timestamp, service, type, label, state
        );
        System.out.println(json);
        System.out.flush();
    }
} 

