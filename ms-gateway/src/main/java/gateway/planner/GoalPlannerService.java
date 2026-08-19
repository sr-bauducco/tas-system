package gateway.planner;

import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/context")
public class GoalPlannerService {

    private final GoalKnowledgeBase knowledgeBase;

    public GoalPlannerService(GoalKnowledgeBase knowledgeBase) {
        this.knowledgeBase = knowledgeBase;
    }

    @PostMapping("/{contextId}")
    public Mono<Void> updateEnvironment(@PathVariable String contextId, @RequestParam boolean state) {
        // Triggers the state change in the Knowledge Base
        knowledgeBase.updateContext(contextId, state);
        
        // Returns a strictly non-blocking reactive stream
        return Mono.empty(); 
    }
}