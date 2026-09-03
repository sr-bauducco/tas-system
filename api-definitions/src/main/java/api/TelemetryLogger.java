package api;

import java.io.IOException;
import java.nio.file.*;
import java.util.Map;

public final class TelemetryLogger {
    private static final Path RESULTS = Paths.get(
        System.getenv().getOrDefault("TAS_RESULTS_FILE", "results/msgoald_results.csv"));

    private TelemetryLogger() {}

    public static long simulationTime(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Missing X-Simulation-Time-Ms header");
        }
        return Long.parseLong(value);
    }

    public static synchronized void logBundle(
            String label,
            long startMs,
            long endMs,
            Map<String, String> metadata) {

        try {
            Path parent = RESULTS.getParent();
            if (parent != null) Files.createDirectories(parent);

            if (Files.notExists(RESULTS) || Files.size(RESULTS) == 0) {
                Files.writeString(RESULTS,
                    "scenario,execIndex,plotIndex,label,start,end,type\n",
                    StandardOpenOption.CREATE);
            }

            String row = String.format("%s,%s,%s,%s,%d,%d,bundle%n",
                metadata.getOrDefault("scenario", "1"),
                metadata.getOrDefault("execIndex", "1"),
                metadata.getOrDefault("plotIndex", "-1"),
                label.replace(",", "_"),
                startMs,
                endMs);

            Files.writeString(RESULTS, row, StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND);
        } catch (IOException e) {
            throw new IllegalStateException("Unable to write bundle telemetry", e);
        }
    }
}