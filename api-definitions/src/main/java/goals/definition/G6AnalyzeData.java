package goals.definition;

import goals.request.VitalSign;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;

public interface G6AnalyzeData {
    /**
     * G6: Analyze Data
     * Analyzes a vital sign and decides whether to trigger medical support.
     */
    Mono<FulfillmentStatus> analyze(VitalSign vitals);
}