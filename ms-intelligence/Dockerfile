FROM eclipse-temurin:17-jdk-alpine
VOLUME /tmp
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} app.jar
# Run the application with standard JVM tuning for containers
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-Xmx256m", "-jar", "/app.jar"]