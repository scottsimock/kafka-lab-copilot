
Copilot steps

`/init`
`please run backlog init for this project`
`please create the mcp.json file for backlog`
`merge the contents from CLAUDE.md into copilot-instructions.md`
`/clear`
`/models`
```
Hi. We're now going to setup our coding system. I want it to be a system that uses two types of agents.

1) Agent one will be an orchestrator that acts as the technical lead. The orchestrator is defined by a skill in .github/skills and will only work through the backlog (MCP). It will work with the user to understand the intent, objectives and requirements for the project, and then use that to define the work in the backlog. The orchestrator should use dot notation when creating task ids in the backlog where the name is 'task'-epic#-task#.  This agent MUST NOT DO ANY DEV WORK DIRECTLY.

2) Agent two is the subagent that will be called by the orchestrator and will do work that is described in the backlog. The backlog is the only medium that the requirements can be described to the subagent. If code is written then unit tests must also be written.  

Finally, please edit the copilot-instructions.md file that describes how this system works.

TO create the agents lookup best practies for skills from anthropic.
```

`add this anthropic skill to the project: https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md`

```
We're going to start a project today that will host an application that generates messages to multiple confuent kafka clusters in multiple azure regions and availaibility zones. The first thing I want you to do as the technical lead is to create an epic that has several subtasks all created under epic 1. The purpose of the epic is to research best practices on how to build multi-region and multi-availability zone confluent kakfa clusters in azure running on virtual machines. Use the developer subagents to go to the internet, ao all that research, come back, build out comprehensive documentation as to the approach to deploy and run confluent kafka in azure. For now all I want you to do as tech lead is to build that epic and subtasks as a plan for this research and design epic. Do not do anything else. Once complete, pause.
```

`/fleet You are the tech lead. Please use the orchestrator skill to invoke the developer subagents to complete epic 2 and all the tasks for epic 2. Accomplish all subtasks with your team autonomously`

```
You are working very effectively through the tasks in the backlog, but, the agents are not committing their work to git. Please create a new skill about adhereing to good git hygiene making sure that after each task is completed successfully there is a related git commit. Pleaes update the copilot-instructions for this general project direction, update the orchestrator skill to follow this practice and update the developer agent to follow this practice.
```