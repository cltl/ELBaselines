WikiViews = require('wikiviews');

var entity = process.argv[2];
var startDate = process.argv[3];
var endDate = process.argv[4];
 
WikiViews(entity, startDate, endDate, function(data) {
    console.log(data);
});
