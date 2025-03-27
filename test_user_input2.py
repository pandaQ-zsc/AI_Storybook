async def main(args: Args) -> Output:
    params = args.params
    # 构建输出对象
    ret: Output = {
        "mode_id": params['input'][0]['id']
    }
    return ret