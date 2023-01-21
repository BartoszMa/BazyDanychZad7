const express = require("express");
const recordRoutes = express.Router();
const dbo = require("../db/conn");
const ObjectId = require("mongodb").ObjectId;



recordRoutes.route("/import").post(function(req, response){
    let db_connect = dbo.getDb("products");
    let myobj = req.body;
    db_connect.collection("records").insertMany(myobj, function(err, res){
        if (err) throw err;
        response.json(res);
    });
});


recordRoutes.route("/products").get(function(req, res) {
    let db_connect = dbo.getDb("products");
    let query = {};
    let sort = {};
    let limit = 0;
    let skip = 0;
    let projection = {};
    let sortField = req.query.sortField;
    let sortOrder = req.query.sortOrder;
    let filterField = req.query.filterField;
    let filterValue = req.query.filterValue;
    let limitValue = req.query.limit;
    let skipValue = req.query.skip;
    let projectionValue = req.query.projection;

    if (sortField && sortOrder) {
        sort[sortField] = parseInt(sortOrder);
    }

    if (filterField && filterValue) {
        query[filterField] = filterValue;
    }

    if (limitValue) {
        limit = parseInt(limitValue);
    }

    if (skipValue) {
        skip = parseInt(skipValue);
    }

    if (projectionValue) {
        projection[projectionValue] = 1;
    }

    db_connect.collection("records").find(query).sort(sort).limit(limit).skip(skip).project(projection).toArray(function(err, result) {
        if (err) throw err;
        res.json(result);
    });
});


recordRoutes.route("/products").post(function(req, response){
    let db_connect = dbo.getDb("products");
    let myobj = {
        name: req.body.name,
        price: req.body.price,
        quantity: req.body.quantity
    };
    db_connect.collection("records").
    findOne
    ({name
    : req.body.name}, function(err, result) {
        if (err) throw err;
        if (result) {
            response.json({message: "Product name already exists"});
        } else {
            db_connect.collection("records").insertOne(myobj, function(err, res){
                if (err) throw err;
                response.json(res);
            });
        }
    });
});



recordRoutes.route("/products/:id").put(function(req, response){
    let db_connect = dbo.getDb("products");
    let myquery = { _id: ObjectId(req.params.id) };
    let newvalues = { $set: {name: req.body.name, price: req.body.price, quantity: req.body.quantity, description: req.body.description} };
    db_connect.collection("records").updateOne
    (myquery
    , newvalues, function(err, res) {
        if (err) throw err;
        response.json(res);
    }
    );
});


recordRoutes.route("/products/:id").delete(function(req, response){
    let db_connect = dbo.getDb("products");
    let myquery = { _id: ObjectId(req.params.id) };
    db_connect.collection("records").deleteOne(myquery,
    function(err, res) {
        if (err) throw err;
        response.json(res);
    }
    );
});


recordRoutes.route("/products/report").get(function(req, res) {
    let db_connect = dbo.getDb("products");
    let query = {};
    let sort = {};
    let limit = 0;
    let skip = 0;
    let projection = {};
    let sortField = req.query.sortField;
    let sortOrder = req.query.sortOrder;
    let filterField = req.query.filterField;
    let filterValue = req.query.filterValue;
    let limitValue = req.query.limit;
    let skipValue = req.query.skip;
    let projectionValue = req.query.projection;

    if (sortField && sortOrder) {
        sort[sortField] = parseInt(sortOrder);
    }

    if (filterField && filterValue) {
        query[filterField] = filterValue;
    }

    if (limitValue) {
        limit = parseInt(limitValue);
    }

    if (skipValue) {
        skip = parseInt(skipValue);
    }

    if (projectionValue) {
        projection[projectionValue] = 1;
    }

    db_connect.collection("records").aggregate([
        { $match: { quantity: { $gt: 0 } } },
        { $group: { _id: "$name", total: { $sum: "$quantity" } } }
    ]).toArray(function(err, result) {
        if (err) throw err;
        res.json(result);
    });
}
);

module.exports = recordRoutes;