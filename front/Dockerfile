# Use the official Node.js image as the base image
FROM node:16-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the React app for production
RUN npm run build

# Use an official Nginx image to serve the React app
FROM nginx:alpine

# Create data directory and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy the built React app from the previous stage to the Nginx web server directory
COPY --from=0 /app/build /usr/share/nginx/html

# Expose port 80 to make the app accessible
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]