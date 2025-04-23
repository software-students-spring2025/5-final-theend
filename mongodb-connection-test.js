const { MongoClient } = require('mongodb');
require('dotenv').config();

// Connection URI from environment variables
const uri = process.env.MONGO_URI || "mongodb+srv://tm3995:R1y2F5ks1GqkJslL@healthtracker.vc6hwcx.mongodb.net/?retryWrites=true&w=majority&appName=HealthTracker";

async function testConnection() {
  if (!uri) {
    console.error("ERROR: MONGO_URI environment variable not set");
    console.log("Please create a .env file with your MongoDB Atlas connection string:");
    console.log("MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority");
    process.exit(1);
  }

  const client = new MongoClient(uri);

  try {
    // Connect to the MongoDB cluster
    await client.connect();
    console.log("✅ Successfully connected to MongoDB Atlas");

    // Get database information
    const adminDb = client.db("admin");
    const serverInfo = await adminDb.command({ serverStatus: 1 });
    
    console.log(`MongoDB version: ${serverInfo.version}`);
    console.log(`Connection: ${serverInfo.connections.current} current / ${serverInfo.connections.available} available`);

    // List all databases
    const databasesList = await client.db().admin().listDatabases();
    console.log("\nAvailable databases:");
    databasesList.databases.forEach(db => {
      console.log(` - ${db.name} (${(db.sizeOnDisk / 1024 / 1024).toFixed(2)} MB)`);
    });

    // Check for health_metrics_tracker database
    const hasTrackerDb = databasesList.databases.some(db => db.name === "health_metrics_tracker");
    if (hasTrackerDb) {
      // List collections in health_metrics_tracker
      const db = client.db("health_metrics_tracker");
      const collections = await db.listCollections().toArray();
      
      console.log("\nCollections in health_metrics_tracker:");
      collections.forEach(collection => {
        console.log(` - ${collection.name}`);
      });

      // Get document counts for each collection
      console.log("\nDocument counts:");
      for (const collection of collections) {
        const count = await db.collection(collection.name).countDocuments();
        console.log(` - ${collection.name}: ${count} documents`);
      }
    } else {
      console.log("\n⚠️ health_metrics_tracker database not found");
      console.log("Run the MongoDB setup script to create the database and collections");
    }
  } catch (error) {
    console.error("❌ Error connecting to MongoDB Atlas:", error);
  } finally {
    // Close the connection
    await client.close();
    console.log("\nConnection closed");
  }
}

// Run the test
testConnection().catch(console.error);
