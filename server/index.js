const fs = require("fs");
const cors = require("cors");
const express = require('express');
const bodyParser = require('body-parser')
const app = express();
const mongoContext = require('./mongoContext');
const {start} = require("repl");

app.use(bodyParser.json())
app.use(cors());

app.post('/api/search/', async (req, res) => {

   var ret = [];
   var query = {};

   if(req.body){
      if (req.body.ticket) query['ticket'] = req.body.ticket
      if (req.body.author) query['author'] = req.body.author
      if(req.body.dateRange.startDate != '' && req.body.dateRange.startDate != null){
         query['date'] = {}
         query['date']['$gte'] = new Date(req.body.dateRange.startDate)
      }
         
      if(req.body.dateRange.endDate != '' && req.body.dateRange.endDate != null){
         if (!('date' in query)) query['date'] = {}
         query['date']['$lte'] = new Date(req.body.dateRange.endDate)
      }
      if(req.body.file_name) query['file_name'] = req.body.file_name
      if(Object.keys(query).length > 0){
         ret = await mongoContext.collections.checkins.find(query).toArray()
      }
   } else{
      ret = []
   }

   res.send(ret)
})

let resetQuery = (startDate, endDate) => {

   var query = {}

   if(startDate != '' && startDate != null){
      query['date'] = {}
      query['date']['$gte'] = new Date(startDate)
   }  
   if(endDate != '' && endDate != null){
      if (!('date' in query)) query['date'] = {}
      query['date']['$lte'] = new Date(endDate)
   }
   return query;
}

app.post('/api/suggestions/', async (req, res) => {

   var startDate = req.body.dateRange.startDate;
   var endDate = req.body.dateRange.endDate;

   var ret = {}
   var query = resetQuery(startDate, endDate);

   Object.keys(req.body).forEach(k => { if (k == '') req.body[k] = null })

   if(req.body){
      if(req.body.author) query['author'] = req.body.author;
      if(req.body.file_name) query['file_name'] = req.body.file_name;
   }
   
   ret['tickets'] = [{data: await mongoContext.collections.checkins.distinct("ticket", query)}]

   query = resetQuery(startDate, endDate)
   if(req.body){
      if(req.body.ticket) query['ticket'] = req.body.ticket;
      if(req.body.file_name) query['file_name'] = req.body.file_name;
   }
   ret['authors'] = [{data: await mongoContext.collections.checkins.distinct("author", query)}]

   query = query = resetQuery(startDate, endDate)
   if(req.body){
      if(req.body.ticket) query['ticket'] = req.body.ticket;
      if(req.body.author) query['author'] = req.body.author;
   }
   ret['files'] = [{data: await mongoContext.collections.checkins.distinct("file_name", query)}]

   res.send(ret)
})

// Handles index.html
app.use(express.static(__dirname + "/public"));
app.get(/.*/, (req, res) => {
   res.sendFile(__dirname + "/public/index.html");
});


// Listen on specified port
const port = process.env.PORT || 8616;
app.listen(port, () => {
   console.log("Server started on port " + port);
});