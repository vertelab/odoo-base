/* @odoo-module */
//import { parseEmail } from "@mail/utils/common/format";

/**
 * splits the string and find all the invalid emails from it.
 *
 * @param {string}
 * @return {object}
 */

export function parseEmail(text) {
    if (!text) {
        return;
    }
    let result = text.match(/"?(.*?)"? <(.*@.*)>/);
    if (result) {
        const name = (result[1] || "").trim().replace(/(^"|"$)/g, "");
        return [name, (result[2] || "").trim()];
    }
    result = text.match(/(.*@.*)/);
    if (result) {
        return [String(result[1] || "").trim(), String(result[1] || "").trim()];
    }
    return [text, false];
}

function findInvalidEmailFromText(emailStr){
    const emailList = emailStr.split('\n');
    const invalidEmails = emailList.filter(email => email !== '' && !parseEmail(email.trim())[1]);
    const emailInfo = {
        'invalidEmails': invalidEmails,
        'emailList': emailList,
    }
    return emailInfo
}

export {
    findInvalidEmailFromText
};
