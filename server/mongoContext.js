var collections = {};
const MongoClient = require("mongodb").MongoClient;
const ObjectId = require("mongodb").ObjectID;

MongoClient.connect("mongodb://mislnxnp014:27017/:27017?readPreference=primary&appname=MongoDB%20Compass&ssl=false", {
   useUnifiedTopology: true,
})
   .then((client) => {
      const cvs_db = client.db("cvs");
      collections["checkins"] = cvs_db.collection("checkins");
      console.log("Connected to MongoDb");
   })
   .catch((error) => {
      console.log(error);
   });

module.exports = {
   ObjectId,
   collections,
};