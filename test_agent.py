from AgentChart import AgentChart
from AgentData import AgentData

if __name__ == "__main__":

    # test model

    import asyncio

    agent_data = AgentData(model="gemini-2.5-flash")
    result_data = asyncio.run(
        agent_data.chat("ใช้ mcp tool execute_sql นับจำนวนประชากรทั้งหมด แยกรายหมู่บ้าน"),
    )
    print(result_data.output)

    agent_chart = AgentChart(model="openrouter/horizon-beta")
    result_chart = asyncio.run(
        agent_chart.chat(
            "แสดงกราฟแท่ง",
            """ หมู่ที่,จำนวนหลังคาเรือน
                01,191
                02,111
                03,101
                04,81
                05,102
                06,173 """,
        )
    )
    print(result_chart.output)
