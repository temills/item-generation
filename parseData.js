// This file holds functions for parsing the data 

    //reformat data before saving
    function reformat_data(data) {
        data2 = {};
        bigData = [];
        data2.exp_type = remove_quotes(data[0].exp_type);
        responses = str_to_dict(data[2].responses);
        data2.subject_id = responses.subject_id;
        if(data2.exp_type == "generation") {
            for (var i=4; i<14; i++) {
                data2.order = i-3;
                responses = str_to_dict(data[i].responses);
                data2.category = Object.keys(responses)[0];
                //can expand into response1, response2, ...
                data2.response = Object.values(responses);
                data2.rt = remove_quotes(data[i].rt);
                demo1 = str_to_dict(data[data.length-2].responses); //CHANGE TO -3 AFTER ADDING END TRIAL
                data2.age = Object.values(demo1)[0];
                data2.language = Object.values(demo1)[1];
                data2.nationality = Object.values(demo1)[2];
                data2.country = Object.values(demo1)[3];
                demo2 = str_to_dict(data[data.length-1].responses); //CHANGE TO -2 AFTER ADDING END TRIAL
                data2.gender = Object.values(demo2)[0];
                data2.student = Object.values(demo2)[1];
                data2.education = Object.values(demo2)[2];
                bigData.push(data2);
            }            
        }
        else {
            for (var i=4; i<24; i+=2) {
                data2.order = (i/2)-1;
                responses1 = str_to_dict(data[i].responses);
                data2.question = Object.keys(responses1)[0];
                data2.response = Object.values(responses1);
                data2.rt_response = remove_quotes(data[i].rt);
                responses2 = str_to_dict(data[i+1].responses);
                data2.category = Object.keys(responses2)[0];
                //can expand into consideration1, consideration2, ...
                data2.considerations = Object.values(responses2);
                data2.rt_considerations = remove_quotes(data[i+1].rt);
                demo1 = str_to_dict(data[data.length-3].responses); //CHANGE TO -3 AFTER ADDING END TRIAL
                data2.age = Object.values(demo1)[0];
                data2.language = Object.values(demo1)[1];
                data2.nationality = Object.values(demo1)[2];
                data2.country = Object.values(demo1)[3];
                demo2 = str_to_dict(data[data.length-2].responses); //CHANGE TO -2 AFTER ADDING END TRIAL
                data2.gender = Object.values(demo2)[0];
                data2.student = Object.values(demo2)[1];
                data2.education = Object.values(demo2)[2];
                bigData.push(data2);
            }
        }
        makeQuery(bigData);
    }

    function str_to_dict(str) {
        dict = {};
        if(str[0] == "{") {
            key = "";
            for(start = 2; start<str.length; start++) {
                end = start;
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
    table = data[0].exp_type;
    for(key in data[0].keys()) {
        keys.concat(key + ", ")
    }
    keys = "(" + keys.substring(0, keys.length()-2) + ")";
    valuesList = []
    i = 0;
    for (dict in data) {
        for(val in dict.values()) {
            valuesList[i].concat("'" + val + "', ")
        }
        i++;
    }
    valuesStr = ""
    for (i=0; i<valuesList.length(); i++) {
        values = valuesList[i];
        values = "(" + values.substring(0, values.length()-2) + ")";
        valuesStr = valuesStr + values + ", ";
    }
    valuesStr = valuesStr.substring(0, valuesStr.length()-2);
    return "INSERT INTO " + table + " " + keys + "VALUES " + valuesStr + ";";
}