// This file holds functions for parsing the data 

    //reformat data before saving
function reformat_data(data) {
    var bigData = [];
    data2 = {};
    data2.exp_type = remove_quotes(data[0].exp_type);
    if(data2.exp_type == "generation") {
        for (var i=4; i<14; i++) {
            var data2 = {};
            var responses = str_to_dict(data[2].responses);
            data2.subject_id = responses.subject_id;
            data2.exp_type = remove_quotes(data[0].exp_type);
            data2.turk_code = remove_quotes(data[0].turk_code);
            data2.trial_order = i-3;
            responses = str_to_dict(data[i].responses);
            data2.category = Object.keys(responses)[0];
            //data2.response = Object.values(responses);
            for(var j=1; j<11; j++) {
                var key = "response" + j;
                //key = eval(`response${i}`);
                var res = Object.values(responses)[j-1];
                console.log(res);
                res = res.replace("'", "");
                console.log(res);
                res = res.replace('"', '');
                console.log(res);
                data2[key] = res;
            }
            console.log("ok");
            data2.rt = remove_quotes(data[i].rt);
            var demo1 = str_to_dict(data[data.length-2].responses); //CHANGE TO -3 AFTER ADDING END TRIAL
            data2.age = Object.values(demo1)[0];
            data2.language = Object.values(demo1)[1];
            data2.nationality = Object.values(demo1)[2];
            data2.country = Object.values(demo1)[3];
            var demo2 = str_to_dict(data[data.length-1].responses); //CHANGE TO -2 AFTER ADDING END TRIAL
            data2.gender = Object.values(demo2)[0];
            data2.student = Object.values(demo2)[1];
            data2.education = Object.values(demo2)[2];
            console.log(data2);
            bigData.push(data2);
        }            
    }
    else {
        for (var i=4; i<24; i+=2) {
            var data2 = {};
            data2.exp_type = remove_quotes(data[0].exp_type);
            data2.turk_code = remove_quotes(data[0].turk_code);
            var responses = str_to_dict(data[2].responses);
            data2.subject_id = responses.subject_id;
            data2.trial_order = (i/2)-1;
            var responses1 = str_to_dict(data[i].responses);
            data2.question = Object.keys(responses1)[0];
            var res1 = Object.values(responses1)[0];
            res1 = res1.replace("'", "");
            res1 = res1.replace('"', '');
            data2.response = res1;
            data2.rt_response = remove_quotes(data[i].rt);
            var responses2 = str_to_dict(data[i+1].responses);
            data2.category = Object.keys(responses2)[0];
            //can expand into consideration1, consideration2, ...
            //data2.considerations = Object.values(responses2);
            for(var j=1; j<9; j++) {
                var key = 'consideration' + j;
                var res = Object.values(responses2)[j-1];
                console.log(res);
                res = res.replace("'", "");
                console.log(res);
                res = res.replace('"', '');
                console.log(res);
                data2[key] = res;
            }
            data2.rt_considerations = remove_quotes(data[i+1].rt);
            var demo1 = str_to_dict(data[data.length-2].responses);
            data2.age = Object.values(demo1)[0];
            data2.language = Object.values(demo1)[1];
            data2.nationality = Object.values(demo1)[2];
            data2.country = Object.values(demo1)[3];
            var demo2 = str_to_dict(data[data.length-1].responses);
            data2.gender = Object.values(demo2)[0];
            data2.student = Object.values(demo2)[1];
            data2.education = Object.values(demo2)[2];
            bigData.push(data2);
        }
    }
    return bigData;
}

function str_to_dict(str) {
    var dict = {};
    if(str[0] == "{") {
        var key = "";
        for(var start = 2; start<str.length; start++) {
            var end = start;
            while(true) {
                if(str[end]== "\"") {
                    if(str[end+1] == ":") {
                        key = str.substring(start, end);
                        start = end+2;
                        break;
                    }
                    else if((str[end+1] == ",") ||(str[end+1] == "}")) {
                        dict[key] = str.substring(start, end);
                        start = end+2;
                        break;
                    }
                }
                end++;
            }
        }
    }
    return dict;
}

function remove_quotes(str) {
    if((str[0] == str[str.length-1] == "\"") && (str.length > 1))
        return str.substring(1, str.length-1);
    else
        return str;
}

function remove_spaces(str) {
    for(i=0; i<str.length; i++)
        if(str[i] == " ")   str[i] = "_";
    return str;
}

export function makeQuery(data) {
    console.log("Parsing");
    data = reformat_data(data);
    console.log("done");
    var table = data[0].exp_type;
    var keys = "";
    var keyArr = Object.keys(data[0]);
    for(var i=0; i<keyArr.length; i++) {
        keys = keys.concat(keyArr[i] + ", ");
    }
    keys = "(" + keys.substring(0, keys.length-2) + ")";
    var valuesList = [];
    var x = 0;
    for(var i=0; i<data.length; i++) {
        var dict = data[i];
        valuesList[x] = "";
        var valArray = Object.values(dict);
        for(var j=0; j<valArray.length; j++) {
            valuesList[x] = valuesList[x].concat("'" + valArray[j] + "', ");
        }
        x++;
    }
    var valuesStr = ""
    for (var i=0; i<valuesList.length; i++) {
        var values = valuesList[i];
        values = "(" + values.substring(0, values.length-2) + ")";
        valuesStr = valuesStr + values + ", ";
    }
    valuesStr = valuesStr.substring(0, valuesStr.length-2);
    //console.log(valuesStr);
    return "INSERT INTO " + table + keys + " " + "VALUES " + valuesStr + ";";
}