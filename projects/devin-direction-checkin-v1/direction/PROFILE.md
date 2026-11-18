# Company research profile: Apple Messages "Check In"

Retrieved 2026-11-18.

| # | Fact | Source | Kind |
|---|---|---|---|
| F1 | Check In lets a user automatically notify a friend that their iPhone has arrived. | Apple iPhone User Guide, "Use Check In on iPhone to let your friends know you've arrived" (support.apple.com/guide/iphone/use-check-in-iphc143bb7e9/ios) | observed |
| F2 | Requires iOS 17 or later for sender and recipient. | same | observed |
| F3 | Start: in a conversation tap +, More, Check In, then Edit. | same | observed |
| F4 | Mode "When I Arrive": destination, travel mode (driving, transit, walking), Add Extra Time. | same; screenshot alt text "estimated travel times for Driving, Transit, and Walking ... Add Extra Time" | observed |
| F5 | Mode "After a timer": a set period, e.g. meeting someone new. | same | observed |
| F6 | On successful arrival the Check In completes automatically and notifies the friend. | same | observed |
| F7 | If not progressing / not arriving and the user doesn't respond to prompts, journey details are sent to the friend (location, battery, cellular signal; Full adds route and last unlock). | same + Settings > Apps > Messages > Check In Data | observed |
| F8 | Shared information is end-to-end encrypted. | Apple Newsroom, "iOS 17 makes iPhone more personal and intuitive", 2023-06-05 | observed |
| I1 | The emotional promise is the friend NOT having to ask "are you home?". | inference from F1/F6 | inference |
| G1 | No Apple fonts, SF Symbols or real Check In card artwork are bundled; card geometry is an authored approximation, Arial fallback per skill. | skill disclosure | gap |
| G2 | Exact Check In card layout/copy ("Check In", "Ended"/"Arrived" labels) not verified against a device screenshot. Copy used in film is limited to phrases in the guide. | gap |

Story supported by evidence: need (late walk home) -> start Check In inside the thread -> the user stops interacting (walks) -> arrival -> friend notified automatically.
No claim about safety outcomes, emergency services, or Android.
