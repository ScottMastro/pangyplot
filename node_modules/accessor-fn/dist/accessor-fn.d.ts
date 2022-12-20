type AccessorFn = (item: any) => any;

declare function accessor(
  accessorParam: string | AccessorFn | any
): AccessorFn;

export default accessor;
