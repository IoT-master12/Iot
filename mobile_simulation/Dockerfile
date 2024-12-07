mobile-client:
    image: nginx:alpine
    container_name: mobile-client
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./mobile_simulation/index.html:/usr/share/nginx/html/index.html
    depends_on:
      - flask-server
    networks:
      - iot-network
