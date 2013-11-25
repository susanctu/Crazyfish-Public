Crazyfish
=========

Crazyfish private repository. 
This repository contains the source code and resources for the first prototype
of the crazyfish website. The website uses the Django framework on the back
end, and Bootstrap (TBD?) for the front end. 

The repository contains the following elements: 
   + [cfsite](./cfsite): the basic Django website folder. Contains the global
   website settings (database, apps, etc), as well as the url structure. 
   + [events](./events): the app which handles events. All the event-related 
   stuff, in terms of database, admin, serving views is in here. 
   + [database_temp](./database_temp): a temporary folder which hosts a dummy
   sqlite database for testing purposes. It's easier to deploy the website
   using this as python ships by default with sqlite. 
   + [mocks](./mocks): website design goes in here.
