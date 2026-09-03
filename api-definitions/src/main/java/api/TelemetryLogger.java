package api;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;
import java.time.Instant;
import java.util.Locale;

public class TelemetryLogger {
    // 1. Caminho ABSOLUTO para casar perfeitamente com o volume do Docker
    private static final String FILE_PATH = "/telemetry/bundle_activations.jsonl";
    
    public static synchronized void logExecution(String traceId, String bundleName, String endpoint, double durationMs) {
        String timestamp = Instant.now().toString();
        
        // 2. Usamos Locale.US para formatar o float com ponto, SEM quebrar as vírgulas do JSON
        String jsonLine = String.format(Locale.US,
            "{\"type\": \"execution\", \"timestamp\": \"%s\", \"traceId\": \"%s\", \"bundle\": \"%s\", \"endpoint\": \"%s\", \"durationMs\": %.4f}",
            timestamp, traceId, bundleName, endpoint, durationMs
        );

        writeLog(jsonLine);
    }

    public static synchronized void logEvent(String source, String category, String eventName, String status) {
        String timestamp = Instant.now().toString();
        
        String jsonLine = String.format(Locale.US,
            "{\"type\": \"event\", \"timestamp\": \"%s\", \"source\": \"%s\", \"category\": \"%s\", \"eventName\": \"%s\", \"status\": \"%s\"}",
            timestamp, source, category, eventName, status
        );

        writeLog(jsonLine);
    }

    private static void writeLog(String jsonLine) {
        try {
            File file = new File(FILE_PATH);
            
            // 3. Garante que a pasta /results existe dentro do contêiner antes de salvar
            if (file.getParentFile() != null) {
                file.getParentFile().mkdirs(); 
            }
            
            try (PrintWriter out = new PrintWriter(new FileWriter(file, true))) {
                out.println(jsonLine);
            }
        } catch (IOException e) {
            System.err.println("Falha ao gravar telemetria do GoalD: " + e.getMessage());
        }
    }
}