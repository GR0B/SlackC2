A very basic Slack C2 

What:
Gives a basic command prompt over a Slack channel

Why use Python?
Well this was more created as a PoC for me and not something to be used in a real engagement. I wanted something very simple, cross platform (Windows/Linux), and easy to tweak on the fly. 

Why use Slack as a Command and Control server? 
Well if you are a red teaming, you most likely want to keep suspicion low. This may mean you want to not use suspicious  domains or services that may alert the blue team.  
So why not reuse a legitimate service used by many organisations to communicate, one that also offers encryption and is real-time. 
Well that is where Slack can be a good choice. Is already used by many teams so not going to stand out on the firewall, has SSL/TLS encryption so has a basic layer of encryption on the data stream.

Features:
-Coded Python
-Only uses common/builtin Python modules (Slack messages uses requests, not module)   
-Jitter on Slack polling
-Onconnect the agent posts the external IP, username, hostname to the Slack channel
-Agent runs commands (Windows/Linux) and returns the command output as a threaded reply in Slack.   

Requirements:
You are going to need to have a Slack server you control, then create a bot with the Channel:history and Chat:write permissions (to get a bot API key)
