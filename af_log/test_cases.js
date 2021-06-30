// These test cases are written to be manually run in the browser.

// SETUP
odoo.define('foo.bar.gazonk', function(require){
    rpc=require('web.rpc');
    session = require('web.session');})

var TEST_PERSONS = [
    'Horus Lupercal',
    'Roboute Guilliman',
    'Ferrus Manus'
];


var data = {
    model: 'res.partner',
    method: 'search',
    args: [[['name', 'in', TEST_PERSONS]]],
};

rpc.query(data).then(function(res){
    if (_.isEmpty(res)){
        console.log('Cleared test data.');
    } else {
        data.method = 'unlink';
        data.args = [res];
        rpc.query(data).then(function(res){
            console.log('Cleared test data.');
        });
    }
});

// Vänta på raderingen

data.method = 'search';
data.args = [[['is_jobseeker', '=', true]]];
data.kwargs = {limit: 3};
var js_ids;
var partner_ids;

// TODO: Switch to dedicated test persons. This is bad when testing DELETE.
rpc.query(data).then(
    function(res){
        js_ids = res;
        console.log('jobseekers read')});
data.args = [[['is_jobseeker', '=', false]]];
rpc.query(data).then(
    function(res){
        partner_ids = res;
        console.log('partners read')});

// Vänta på inläsningarna




//CREATE

//Två admin och en vanlig
var data = {
    model: 'res.partner',
    method: 'create',
    args: [[
        {
            name: 'Horus Lupercal',
            is_jobseeker: true},
        {
            name: 'Roboute Guilliman',
            is_jobseeker: false}]]};
rpc.query(data);

//En admin och en vanlig
data.args = [{
    name: 'Ferrus Manus',
    is_jobseeker: true}];
rpc.query(data);

// READ
data = {
    model: 'res.partner',
    method: 'read',
    args: [
        js_ids,
        ['name', 'user_id', 'meeting_ids']]};

// Tre vanliga
rpc.query(data);

data.args[0] = js_ids[0];

// En vanlig
rpc.query(data);

data.args[0] = partner_ids;

// Nada
rpc.query(data);

data.args[0] = js_ids;
data.args[0].concat(partner_ids);

// Tre vanliga
rpc.query(data);

data.args[0] = [];

// Nada
rpc.query(data);

data.args[0] = 'balupas';

// Nada
rpc.query(data);


// export
var export_data = {
    "model":"res.partner",
    "fields":[
        {"name":"id","label":"External ID"},
        {"name":"display_name","label":"Display Name"},
        {"name":"email","label":"Email"},
        {"name":"phone","label":"Phone"}],
    "ids":js_ids,
    "domain":[["is_jobseeker","=",true]],
    "context":{"lang":"sv_SE","tz":"Europe/Stockholm"},
    "import_compat":false};

// Tre vanliga
session.get_file({
    url: '/web/export/xls',
    data: {data: JSON.stringify(export_data)}
});

// Tre vanliga
session.get_file({
    url: '/web/export/csv',
    data: {data: JSON.stringify(export_data)}
});

export_data.ids = partner_ids;

// Nada
session.get_file({
    url: '/web/export/xls',
    data: {data: JSON.stringify(export_data)}
})
// Nada
session.get_file({
    url: '/web/export/csv',
    data: {data: JSON.stringify(export_data)}
})

export_data.ids = export_data.ids.concat(js_ids);
// Tre vanliga
session.get_file({
    url: '/web/export/xls',
    data: {data: JSON.stringify(export_data)}
})
// Tre vanliga
session.get_file({
    url: '/web/export/csv',
    data: {data: JSON.stringify(export_data)}
})


// UPDATE

var data = {
    model: 'res.partner',
    method: 'write',
    args: [js_ids, {'street': 'Testgatan 123'}]};

// Tre vanliga, tre admin
rpc.query(data);

data.args[0] = partner_ids;
data.args[1].street = 'Testgatan 456';
// Tre admin
rpc.query(data);

data.args[0] = partner_ids.concat(js_ids);
data.args[1].street = 'Testgatan 789';
// Tre vanliga, sex admin
rpc.query(data);

data.args[0] = partner_ids[0];
data.args[1].street = 'Testgatan 321';
// En admin
rpc.query(data);

data.args[0] = js_ids[0];
data.args[1].street = 'Testgatan 654';
// En vanlig, en admin
rpc.query(data);


// SEARCH
data = {
    model: 'res.partner',
    method: 'search_read',
    args: [[['is_jobseeker', '=', true]], ['name']],
    kwargs: {limit: 3}};

// En vanlig (tre träffar)
rpc.query(data);

// Nada
data.args[0] = [['is_jobseeker', '=', false]];
rpc.query(data);

// En vanlig (tre träffar)
data.args[0] = [['id', 'in', js_ids.concat(partner_ids)]];
data.kwargs = {};
rpc.query(data);


// TODO: Make these tests not delete random partners.
// DELETE
data.method = 'unlink';
data.args = [[js_ids[0]]];

// En vanlig, en admin
rpc.query(data);

data.args[0] = [partner_ids[0]];
// En admin
rpc.query(data);

data.args[0] = [partner_ids[1], partner_ids[2], js_ids[1]];
// Tre admin, en vanlig
rpc.query(data);

data.args[0] = js_ids[1];
// En admin, en vanlig
rpc.query(data);
