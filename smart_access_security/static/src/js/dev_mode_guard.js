/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { browser } from "@web/core/browser/browser";

// Guard developer mode URL parameters
if (window.location.search.includes("debug=")) {
    rpc("/web/dataset/call_kw/res.users/check_user_dev_mode_allowed", {
        model: "res.users",
        method: "check_user_dev_mode_allowed",
        args: [],
        kwargs: {},
    }).then((allowed) => {
        if (!allowed) {
            // Strip debug query parameter and reload clean URL
            const url = new URL(window.location.href);
            url.searchParams.delete("debug");
            browser.location.href = url.toString();
        }
    }).catch(() => {});
}
