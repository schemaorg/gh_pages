#!/usr/bin/env python3

properties = [
    ("accountablePerson", "CreativeWork", "Specifies the Person that is legally accountable for the CreativeWork."),
    ("acquiredFrom", "OwnershipInfo", "The organization or person from which the product was acquired."),
    ("actor", "Clip, CreativeWorkSeason, Episode, Event, Movie, MovieSeries, PodcastSeries, RadioSeries, TVSeries, VideoGame, VideoGameSeries, VideoObject", "An actor, e.g. in TV, radio, movie, video games etc., or in an event."),
    ("agent", "Action", "The direct performer or driver of the action (animate or inanimate)."),
    ("alumni", "EducationalOrganization, Organization", "Alumni of an organization."),
    ("artist", "ComicIssue, ComicStory, VisualArtwork", "The primary artist for a work in a medium other than pencils or digital line art."),
    ("athlete", "SportsTeam", "A person that acts as performing member of a sports team."),
    ("attendee", "Event", "A person or organization attending the event."),
    ("author", "CreativeWork, Rating", "The author of this content or rating."),
    ("awayTeam", "SportsEvent", "The away team in a sports event."),
    ("bccRecipient", "Message", "A sub property of recipient. The recipient blind copied on a message."),
    ("bookingAgent", "Reservation", "The entity that holds the reservation."),
    ("borrower", "LendAction", "A sub property of participant. The person that borrows the object being lent."),
    ("broker", "Invoice, Order, Reservation, Service", "An entity that arranges for an exchange between a buyer and a seller."),
    ("buyer", "SellAction", "A sub property of participant. The participant/person/organization that bought the object."),
    ("byArtist", "MusicAlbum, MusicRecording", "The artist that performed this album or recording."),
    ("candidate", "VoteAction", "A sub property of object. The candidate subject of this action."),
    ("ccRecipient", "Message", "A sub property of recipient. The recipient copied on a message."),
    ("character", "CreativeWork", "Fictional person connected with a creative work."),
    ("children", "Person", "A child of the person."),
    ("coach", "SportsTeam", "A person that acts in a coaching role for a sports team."),
    ("colleague", "Person", "A colleague of the person."),
    ("colorist", "ComicIssue, ComicStory, VisualArtwork", "The individual who adds color to inked drawings."),
    ("composer", "Episode, Event, Movie, MovieSeries, MusicComposition, RadioSeries, TVSeries, VideoGame, VideoGameSeries, VideoObject", "The person or organization who wrote a composition."),
    ("contributor", "CreativeWork, Event", "A secondary contributor to the CreativeWork or Event."),
    ("creator", "CreativeWork, UserComments", "The creator/author of this CreativeWork."),
    ("creditedTo", "MusicRelease", "The group the release is credited to."),
    ("customer", "Invoice, Order", "Party placing the order or paying the invoice."),
    ("director", "Clip, CreativeWorkSeason, Episode, Event, Movie, MovieSeries, RadioSeries, TVSeries, VideoGame, VideoGameSeries, VideoObject", "A director of e.g. TV, radio, movie, video gaming etc. content."),
    ("editor", "CreativeWork", "Specifies the Person who edited the CreativeWork."),
    ("employee", "Organization", "Someone working for this organization."),
    ("endorsee", "EndorseAction", "A sub property of participant. The person/organization being supported."),
    ("endorsers", "Diet", "People or organizations that endorse the plan."),
    ("followee", "FollowAction", "A sub property of object. The person or organization being followed."),
    ("founder", "Organization", "A person who founded this organization."),
    ("funder", "CreativeWork, Event, MonetaryGrant, Organization", "A person or organization that supports (sponsors) something through some kind of financial contribution."),
    ("homeTeam", "SportsEvent", "The home team in a sports event."),
    ("illustrator", "Book", "The illustrator of the book."),
    ("inker", "ComicIssue, ComicStory, VisualArtwork", "The individual who traces over the pencil drawings in ink."),
    ("instructor", "CourseInstance", "A person assigned to instruct or provide instructional assistance for the CourseInstance."),
    ("knowsAbout", "Organization, Person", "Of a Person, and less typically of an Organization, to indicate a topic that is known about."),
    ("landlord", "RentAction", "A sub property of participant. The owner of the real estate property."),
    ("lender", "LendAction", "A sub property of participant. The person that lends the object being borrowed."),
    ("letterer", "ComicIssue, ComicStory, VisualArtwork", "The individual who adds lettering, including speech balloons and sound effects, to artwork."),
    ("lyricist", "MusicComposition", "The person who wrote the words."),
    ("member", "Organization, ProgramMembership", "A member of an Organization or a ProgramMembership."),
    ("merchant", "Order", "merchant is an out-dated term for seller."),
    ("musicBy", "Clip, Episode, Event, Movie, MovieSeries, RadioSeries, TVSeries, VideoGame, VideoGameSeries, VideoObject", "The composer of the soundtrack."),
    ("organizer", "Event", "An organizer of an Event."),
    ("parent", "Person", "A parent of this person."),
    ("participant", "Action", "Other co-agents that participated in the action indirectly."),
    ("penciler", "ComicIssue, ComicStory, VisualArtwork", "The individual who draws the primary narrative artwork."),
    ("performer", "Event", "A performer at the event—for example, a presenter, musician, musical group or actor."),
    ("producer", "CreativeWork", "The person or organization who produced the work."),
    ("provider", "CreativeWork, EducationalOccupationalProgram, Invoice, ParcelDelivery, Reservation, Service, Trip", "The service provider, service operator, or service performer."),
    ("publisher", "Book, CreativeWork, NewsMediaOrganization, PublicationEvent", "The publisher of the creative work."),
    ("readBy", "Audiobook", "A person who reads (performs) the audiobook."),
    ("recipient", "AuthorizeAction, CommunicateAction, DonateAction, GiveAction, Message, PayAction, ReturnAction, SendAction, TipAction", "A sub property of participant. The participant who is at the receiving end of the action."),
    ("recognizedBy", "EducationalOccupationalCredential", "An organization that acknowledges the validity, value or utility of a credential."),
    ("reviewedBy", "WebPage", "People or organizations that have reviewed the content on this web page for accuracy and/or completeness."),
    ("sdPublisher", "CreativeWork", "Indicates the party responsible for generating and publishing the current structured data markup."),
    ("seeks", "JobPosting", "A pointer to products or services sought by the organization or person (demand)."),
    ("seller", "BuyAction, Demand, Flight, Offer, Order", "An entity which offers (sells / leases / lends / loans) the services / goods."),
    ("sender", "Message, ReceiveAction", "A sub property of participant. The participant who is at the sending end of the action."),
    ("siblings", "Person", "A sibling of the person."),
    ("sponsor", "CreativeWork, Event, Grant, MedicalStudy, Organization", "A person or organization that supports a thing through a pledge, promise, or financial contribution."),
    ("spouse", "Person", "The person's spouse."),
    ("toRecipient", "Message", "A sub property of recipient. The recipient who was directly sent the message."),
    ("translator", "CreativeWork, Event", "Organization or person who adapts a creative work to different languages."),
    ("underName", "Reservation, Ticket", "The person or organization the reservation or ticket is for."),
    ("vendor", "BuyAction", "vendor is an out-dated term for seller."),
    ("winner", "LoseAction", "A sub property of participant. The winner of the action.")
]

for prop, types, desc in properties:
    types_with_links = []
    for t in types.split(", "):
        types_with_links.append(f'<a href="/{t}" class="type-link">{t}</a>')
    types_html = ", ".join(types_with_links)
    
    print(f'''                        <tr>
                            <td><span class="property-name"><a href="/{prop}">{prop}</a></span></td>
                            <td>{types_html}</td>
                            <td>{desc}</td>
                        </tr>''')