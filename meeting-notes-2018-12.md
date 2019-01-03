# 2018-12 Meeting Notes  

Most of the meeting's technical aspects were about the Dashboard;  

Breaking the Dashboard down, the dash will be made up of cards, each of which will be used to display some form of data (ideally real-time/current, etc.).  
When applicable, the data shown by the cards should be customizable, based on the user's address.  
This is addressed via search input asking for said data.  
Specifically, we are not going to ask for user geo via browser because of how wonky the experience is cross-browser/platform.  
The number/type of cards is not set in stone, anything applicable I would assume is game, but we should also be selective. 
Below is the first iteration of whiteboarding:  
![Dashboard WhiteBoarding Version 01](https://raw.githubusercontent.com/rvacivtech/rva_dash/master/resources/dashboard-whiteboard-2018-12-0359-crop-w0900.jpg)  
The defined cards so far are: Crime, Weather, Property, Calendar, Government Reps, and City Actions.
Input and/or data points are best described in the pix I took, which I'll post soon.  
As an example, the crime card will show some default data; perhaps felony assaults over the past month.  
Iterating on the current data is a great way to show context; in this case we could show what they were five-ten years ago.  
Should the user provide their address, we can double down on the data points:  
To continue this example, show felonious assaults recently occuring around them.  
Below is a fleshed out version of the whiteboarding:  
![Dashboard Whiteboarding Version 01 Fleshed Out](https://raw.githubusercontent.com/rvacivtech/rva_dash/master/resources/dashboard-whiteboard-2018-12-0361-crop-w0900.jpg)   
Once this correctly in the repo, each card will need a dedicated space for sharing ideas/thoughts around data points, as well as a space for sharing ideas for cards. preferably the same space*.  

## Current Card thoughts/discussions:  

### Weather  
Show current weather.
Compare to last year-five-years-etc.
Personalize with address data.  
[Good example of a way to iterate over weather day, also a potential ally](https://twitter.com/jer_science/status/1080495395959177216?s=12)  

### Property  
Show increase in variables: sales, transfers, values, etc.
Compare to last year-five-years-etc.
Personalize with address data.  

Maybe we should add/include Housing with Property?  
One idea for tracking an input would be tracking evictions, [inspiration and possible ally](https://twitter.com/RVAEvictionLab/status/1080489955137327104)  

### Calendar  
Show city government events for the day.  


### Government Representatives  
Bios, contact information.
Latest actions taken.  

### City Actions  
Council Meeting Agendas, Contracts, actions taken, etc.  


## Technical Considerations  
Nothing concrete; considering the use-case, I reckon this will be JavaScript for the most part.  
I can see benefits in using some server side rendering here; I think it depends on how interactive we want this to be.  
If there's not much updating after pageload, as in, the cards mostly do nothing once they are rendered, I would lean more into serverland. I can't think of many that would need functionality, but I don't think we've touched the surface of what
is possible.  
Basically, I don't want to optimize prematurely, nor pigeonhole us.  
The flip is, considering how the functionality could be tied to JavaScript, just use JavaScript.  

Whichever route(s) we choose, I think its ideal we put UX first and preference aside.  
That's really easy for me to say considering my thoughts on React/Angular, I know.  
I just want to be clear that if anyone has any valid input regarding all of this, lets chat this up. 
The only wrong opinion/thought is the one you don't share, in my opinion. We're all learning + arrived via different paths.  
Determining some specifications will be one way to accomplish this, or at the very least wittle our options down.  
Starting with who are target audience(s) are, what user-agents and browsers are we supporting?  

Considering the stark differences between data points the city provides, I imagine being as flexible as possible regarding scripts for accessing, scraping, getting the data, will get us further along.  
Providing utilities, templates will be helpful, but really, if your script outputs data in whatever format/spec we require, I say we take it.  
Open States is an example of this, where a bunch of different scripts are ran individually, each pulling down a specific dataset.  
I do think the number of possible data inputs is only going to get larger moving forward; I cannot say with any certainity that a community of user/devs will build around this.  



** this wasn't discussed, just an idea that occurred to me as I was typing this up (Albert).
