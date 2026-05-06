package goals.definition;

import goals.request.VitalSign;
import reactor.core.publisher.Mono;
import api.FulfillmentStatus;

public interface G6AnalyzeData {
    // Goal G6: Analyze Data
    Mono<FulfillmentStatus> analyze(VitalSign vitals); 
}