package api;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;
import java.time.Instant;

public class TelemetryLogger {
    // Caminho que será mapeado como volume compartilhado no Docker
    private static final String FILE_PATH = "results/bundle_activations.jsonl";
    
    // Método para registrar o tempo de execução e a troca de contexto (usado pelos filtros)
    public static synchronized void logExecution(String traceId, String bundleName, String endpoint, double durationMs) {
        String timestamp = Instant.now().toString();
        
        String jsonLine = String.format(
            "{\"type\": \"execution\", \"timestamp\": \"%s\", \"traceId\": \"%s\", \"bundle\": \"%s\", \"endpoint\": \"%s\", \"durationMs\": %.4f}",
            timestamp, traceId, bundleName, endpoint, durationMs
        ).replace(",", "."); // Garante a formatação correta do ponto flutuante

        writeLog(jsonLine);
    }

    // Método para registrar eventos de disponibilidade e falhas (usado pelo Gateway)
    public static synchronized void logEvent(String source, String category, String eventName, String status) {
        String timestamp = Instant.now().toString();
        
        String jsonLine = String.format(
            "{\"type\": \"event\", \"timestamp\": \"%s\", \"source\": \"%s\", \"category\": \"%s\", \"eventName\": \"%s\", \"status\": \"%s\"}",
            timestamp, source, category, eventName, status
        );

        writeLog(jsonLine);
    }

    // Método auxiliar para isolar a lógica de gravação no arquivo
    private static void writeLog(String jsonLine) {
        try (PrintWriter out = new PrintWriter(new FileWriter(FILE_PATH, true))) {
            out.println(jsonLine);
        } catch (IOException e) {
            System.err.println("Falha ao gravar telemetria do GoalD: " + e.getMessage());
        }
    }
}