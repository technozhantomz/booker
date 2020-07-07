from aiohttp.web import Request, Response, RouteTableDef


routes = RouteTableDef()


@routes.get('/')
async def status(request: Request) -> None:
    return Response(text='Ok')
