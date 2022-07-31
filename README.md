# Blocking Orders by Indian Courts 

[![Generic badge](https://img.shields.io/badge/View_Data_on-Flat_Github-GREEN.svg)](https://flatgithub.com/kaarana/BlockingOrdersByIndianCourts?filename=data%2FBlockingOrders.json)


Department of Telecommunications publishes _Blocking notifications/instructions to Internet Service Licensees under court orders_ at https://dot.gov.in/blocking-notificationsinstructions-internet-service-licensees-under-court-orders. An RSS feed of notifications is available at https://dot.gov.in/taxonomy/term/2883/feed

The purpose of this project is to archive all blocking notifications / instructions and additionally extract and maintain a list of urls / domains blocked by court orders. Such list is useful to check

# TODO

- [ ] Parse the Order PDFs (usually last page) and auto-extract URLs in block notifications
- [ ] Maintain a csv / json of all blocked domains with relevant metadata.
- [ ] Github Actions for checking the RSS periodically and update the data.
- [ ] Convert output to sheets / other formats so that watchdog organizations (like IFF) find it easier to periodically monitor compliance by DoT and ISPs