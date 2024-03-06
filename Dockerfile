FROM openjdk:17-jdk

WORKDIR /app
COPY LunarCore.jar .

VOLUME /app/resources
VOLUME /app/data

VOLUME /app/config.json

EXPOSE 443
EXPOSE 23301

CMD ["java", "-jar", "LunarCore.jar"]
